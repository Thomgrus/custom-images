package main

import (
	"context"
	"log"
	"strings"
	"time"

	"github.com/google/go-github/github"
)

type CommitInfo struct {
	Title      string
	Link       string
	SHA        string
	Author     string
	AuthorName string
	Date       time.Time
}

type ReleaseInfo struct {
	Name    string
	Date    time.Time
	Commits []CommitInfo
}

type CompareInfo struct {
	Owner       string
	Repo        string
	Base        string
	Head        string
	ignoreMerge bool
}

func GetReleaseInfo(compareInfo *CompareInfo, githubToken *string) *ReleaseInfo {
	ctx := context.Background()
	client := GetClient(*githubToken)

	rel, _, err := client.Repositories.GetReleaseByTag(ctx, compareInfo.Owner, compareInfo.Repo, compareInfo.Head)

	if err != nil {
		log.Fatalf("Unable to get release response from github %v", err)
	}

	releaseInfo := &ReleaseInfo{
		Name:    rel.GetTagName(),
		Date:    rel.GetCreatedAt().Time,
		Commits: []CommitInfo{},
	}

	releaseInfo.Commits = findCommitsInfo(compareInfo, client, releaseInfo.Commits)

	return releaseInfo
}

func findCommitsInfo(compareInfo *CompareInfo, client *github.Client, commitInfos []CommitInfo) []CommitInfo {
	ctx := context.Background()
	cmp, _, err := client.Repositories.CompareCommits(ctx,
		compareInfo.Owner, compareInfo.Repo,
		compareInfo.Base, compareInfo.Head,
	)

	if err != nil {
		log.Fatalf("Unable to get compare response from github %v", err)
	}

	commitsRead := len(cmp.Commits)
	commitsToProcess := *cmp.TotalCommits

	log.Printf("Comparison %d remaining\n", commitsToProcess)

	commitCompareCallInfos := []CommitInfo{}
	for _, commit := range cmp.Commits {
		if compareInfo.ignoreMerge && len(commit.Parents) > 1 {
			// this is a merge commit ignore it
			continue
		}
		commitInfo := &CommitInfo{
			Title:      strings.Split(commit.GetCommit().GetMessage(), "\n")[0],
			Link:       commit.GetHTMLURL(),
			SHA:        *commit.SHA,
			Author:     commit.GetAuthor().GetLogin(),
			AuthorName: *commit.GetCommit().GetAuthor().Name,
			Date:       *commit.GetCommit().GetAuthor().Date,
		}
		commitCompareCallInfos = append(commitCompareCallInfos, *commitInfo)
	}

	commitInfos = append(commitCompareCallInfos, commitInfos...)

	if commitsToProcess <= commitsRead {
		return commitInfos
	} else {
		compareInfo.Head = *cmp.Commits[0].SHA
		return findCommitsInfo(compareInfo, client, commitInfos[1:])
	}

}
