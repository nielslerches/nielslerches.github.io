import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Set

from pelican import signals
from pelican.contents import Author

import pygit2

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

repository = pygit2.Repository(".git")


def test(article_generator, metadata):
    log.debug("%s", vars(article_generator))

    authors: List[str] = []
    date: datetime = None
    modified: datetime = None

    filepath = Path(article_generator.path).name + "/" + (metadata["slug"] + ".md")
    blame = repository.blame(filepath)
    hunk: pygit2.BlameHunk
    for hunk in blame:
        tzinfo = timezone(timedelta(minutes=hunk.final_committer.offset))
        dt = datetime.fromtimestamp(float(hunk.final_committer.time), tzinfo)
        if modified is None or dt > modified:
            modified = dt
        
        tzinfo = timezone(timedelta(minutes=hunk.orig_committer.offset))
        dt = datetime.fromtimestamp(float(hunk.orig_committer.time), tzinfo)
        if date is None or dt > date:
            date = dt

        if hunk.final_committer.name not in authors:
            authors.append(hunk.final_committer.name)

    metadata["date"] = date
    if modified != date:
        metadata["modified"] = modified
    metadata["authors"] = [Author(author, article_generator.readers.settings) for author in authors]


def register():
    signals.article_generator_context.connect(test)
