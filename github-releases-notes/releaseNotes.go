package main

import (
	"context"
	"log"
	"strings"
	"time"
)

type CommitInfo struct {
	Title  string
	Link   string
	Author string
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

	cmp, _, err := client.Repositories.CompareCommits(ctx,
		compareInfo.Owner, compareInfo.Repo,
		compareInfo.Base, compareInfo.Head,
	)

	if err != nil {
		log.Fatalf("Unable to get compare response from github %v", err)
	}

	for _, commit := range cmp.Commits {
		if compareInfo.ignoreMerge && len(commit.Parents) > 1 {
			// this is a merge commit ignore it
			continue
		}
		commitInfo := &CommitInfo{
			Title:  strings.Split(commit.GetCommit().GetMessage(), "\n")[0],
			Link:   commit.GetHTMLURL(),
			Author: commit.GetAuthor().GetLogin(),
		}
		releaseInfo.Commits = append(releaseInfo.Commits, *commitInfo)
	}

	return releaseInfo
}
