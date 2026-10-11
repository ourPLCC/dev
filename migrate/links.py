"""Rewrite links and issue references in legacy issues and code-repo docs."""
import posixpath
import re
from dataclasses import dataclass, field
from pathlib import Path

ISSUE_DIRS = ("dev-docs/issues", "dev-docs/issues/done", "docs/issues", "docs/issues/done")
RETIRED = ("dev-docs/issues", "dev-docs/roadmap.md", "dev-docs/issue-conventions.md", "docs/issues",
           "bin/issues")
ISSUE_FILE_RE = re.compile(r"^(\d{1,3})-(.+)\.md$")
TOKEN_RE = re.compile(
    r"(?P<wiki>\[\[(?P<wnum>\d{1,3})-(?P<wslug>[^\]\s]+)\]\])"
    r"|(?P<link>\[(?P<text>[^\]]*)\]\((?P<target>[^)\s]+)\))"
    r"|(?<![\w/&#])#0*(?P<num>\d{1,3})\b")
CODE_SPAN_RE = re.compile(r"`+[^`\n]*`+")
AFTER_QUALIFIER_RE = re.compile(r"\s+in\s+`?ourPLCC/([a-z0-9-]+)`?")
BEFORE_QUALIFIER_RE = re.compile(r"([a-z0-9-]+)`?(?:'s)?\s+(?:issue\s+)?$")
NUMBER_TEXT_RE = re.compile(r"(?:issue\s+)?#?0*\d+", re.IGNORECASE)
SCHEME_RE = re.compile(r"^[a-zA-Z][\w+.-]*:")
PR_BEFORE_RE = re.compile(r"\b(?:PR|pull request)\s+$", re.IGNORECASE)


@dataclass(frozen=True)
class IssueRef:
    slug: str
    cr: int


@dataclass
class LinkContext:
    """Where links resolve. `references` None keeps plcc-ng's rule for a bare #N;
    a dict switches on languages-ng's, deciding unqualified #N as {source: {"#N": text}}."""
    repo: str
    repo_root: Path
    issues: dict
    other_offsets: dict
    github: str
    findings: list = field(default_factory=list)
    references: dict = None
    source: str = ""
    defaulted: list = field(default_factory=list)
    unresolved: list = field(default_factory=list)

    def cr_for(self, number, slug, where):
        refs = self.issues.get(number, [])
        if not refs:
            return None
        if slug is not None:
            for ref in refs:
                if ref.slug == slug:
                    return ref.cr
            self.findings.append(
                f"slug mismatch: {where} names {number:03d}-{slug}, "
                f"but {number:03d} is {refs[0].slug}; used CR-{refs[0].cr}")
            return refs[0].cr
        if len(refs) > 1:
            self.findings.append(
                f"ambiguous: {where} refers to #{number:03d}, used by {len(refs)} issues; "
                f"chose CR-{refs[0].cr}")
        return refs[0].cr


def _runs(text):
    """Split text into (is_code, chunk) runs; fenced blocks (with fences) are code."""
    runs, fence = [], False
    for line in text.split("\n"):
        is_fence_line = line.lstrip().startswith("```")
        code = fence or is_fence_line
        if is_fence_line:
            fence = not fence
        if runs and runs[-1][0] == code:
            runs[-1][1].append(line)
        else:
            runs.append((code, [line]))
    return [(code, "\n".join(lines)) for code, lines in runs]


def _exists(ctx, resolved):
    return not resolved.startswith("..") and (Path(ctx.repo_root) / resolved).exists()


def _is_retired(resolved):
    return any(resolved == r or resolved.startswith(r + "/") for r in RETIRED)


def _link(m, file_dir, ctx, full):
    text, target, original = m.group("text"), m.group("target"), m.group(0)
    if SCHEME_RE.match(target) or target.startswith("#"):
        return original
    path, _, anchor = target.partition("#")
    resolved = posixpath.normpath(posixpath.join(file_dir, path))
    issue_file = ISSUE_FILE_RE.match(posixpath.basename(path))
    if issue_file and posixpath.dirname(resolved) in ISSUE_DIRS:
        cr = ctx.cr_for(int(issue_file.group(1)), issue_file.group(2), f"link {target}")
        if cr is None:
            ctx.findings.append(f"broken issue link: {target}")
            return original
        label = f"CR-{cr}"
        return label if NUMBER_TEXT_RE.fullmatch(text.strip()) else f"{text} ({label})"
    if _is_retired(resolved):
        ctx.findings.append(f"link to retired tracker file made plain text: {target}")
        return text
    if not full:
        return original
    if not _exists(ctx, resolved):
        alternative = posixpath.normpath(posixpath.join("dev-docs/issues", path))
        if file_dir.endswith("/done") and _exists(ctx, alternative):
            resolved = alternative
        else:
            ctx.findings.append(f"unresolved link left as is: {target}")
            return original
    suffix = f"#{anchor}" if anchor else ""
    return f"[{text}](../../../{ctx.repo}/{resolved}{suffix})"


def _wiki(m, ctx):
    cr = ctx.cr_for(int(m.group("wnum")), m.group("wslug"), f"link {m.group('wiki')}")
    if cr is None:
        ctx.findings.append(f"broken issue link: {m.group('wiki')}")
        return m.group(0)
    return f"CR-{cr}"


def _bare(m, chunk, ctx):
    number = int(m.group("num"))
    if ctx.references is not None and PR_BEFORE_RE.search(chunk[max(0, m.start() - 20):m.start()]):
        return f"[#{number}]({ctx.github}/pull/{number})"
    repo = None
    after = AFTER_QUALIFIER_RE.match(chunk, m.end())
    if after:
        repo = after.group(1)
    else:
        before = BEFORE_QUALIFIER_RE.search(chunk, max(0, m.start() - 40), m.start())
        if before and (before.group(1) in ctx.other_offsets or before.group(1) == ctx.repo):
            repo = before.group(1)
    if repo and repo != ctx.repo:
        if repo in ctx.other_offsets:
            cr = number + ctx.other_offsets[repo]
            ctx.findings.append(f"qualified cross-repo mention (verify): {repo} #{number} -> CR-{cr}")
            return f"CR-{cr}"
        ctx.findings.append(f"mention of {repo} #{number} left as text (no legacy tracker)")
        return m.group(0)
    cr = ctx.cr_for(number, None, f"#{number}")
    if ctx.references is not None:
        return _decide(m, chunk, ctx, number, cr)
    if cr is not None:
        return f"CR-{cr}"
    return f"[#{number}]({ctx.github}/issues/{number})"


def _decide(m, chunk, ctx, number, cr):
    """languages-ng's unqualified #N: a triage decision, else its own issue, else reported."""
    token = f"#{number}"
    decision = ctx.references.get(ctx.source, {}).get(token)
    if decision is not None:
        return decision
    context = " ".join(chunk[max(0, m.start() - 60):m.end() + 30].split())
    if cr is not None:
        ctx.defaulted.append(f'{ctx.source}: {token} -> CR-{cr} in "{context}"')
        return f"CR-{cr}"
    ctx.unresolved.append(f'{ctx.source}: {token} in "{context}"')
    return m.group(0)


def _process(chunk, file_dir, ctx, full):
    spans = [s.span() for s in CODE_SPAN_RE.finditer(chunk)]

    def replace(m):
        if any(a <= m.start() < b for a, b in spans):
            return m.group(0)
        if m.group("wiki"):
            return _wiki(m, ctx)
        if m.group("link"):
            return _link(m, file_dir, ctx, full)
        if not full:
            return m.group(0)
        return _bare(m, chunk, ctx)

    return TOKEN_RE.sub(replace, chunk)


def _rewrite(text, file_dir, ctx, full):
    return "\n".join(chunk if code else _process(chunk, file_dir, ctx, full)
                     for code, chunk in _runs(text))


def rewrite_issue_body(text, file_dir, ctx):
    return _rewrite(text, file_dir, ctx, full=True)


def rewrite_repo_doc(text, file_dir, ctx):
    return _rewrite(text, file_dir, ctx, full=False)
