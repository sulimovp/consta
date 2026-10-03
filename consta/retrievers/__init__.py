from consta.retrievers.adjacent import AdjacentProjectsRetriever
from consta.retrievers.discourse import DiscourseRetriever
from consta.retrievers.git_activity import GitActivityRetriever
from consta.retrievers.github_issues import GitHubIssuesRetriever
from consta.retrievers.github_prs import GitHubPrsRetriever
from consta.retrievers.huggingface_discussions import HuggingFaceDiscussionsRetriever
from consta.retrievers.process_docs import ProcessDocsRetriever
from consta.retrievers.repo_files import RepoFilesRetriever
from consta.retrievers.vital_signs import VitalSignsRetriever

ALL_RETRIEVERS = [
    GitHubIssuesRetriever(),
    RepoFilesRetriever(),
    GitActivityRetriever(),
    VitalSignsRetriever(),
    AdjacentProjectsRetriever(),
    GitHubPrsRetriever(),
    ProcessDocsRetriever(),
    DiscourseRetriever(),
    HuggingFaceDiscussionsRetriever(),
]
