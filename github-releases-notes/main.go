package main

import (
	"flag"
	"log"
	"os"
)

func main() {
	githubToken := flag.String("token", os.Getenv("GITHUB_TOKEN"), "Github token")
	githubOwner := flag.String("owner", "", "Github repo owner")
	githubRepo := flag.String("repo", "", "Github repo name")
	baseTag := flag.String("base", "", "Github base tag")
	headTag := flag.String("head", "", "Github head tag")
	ignoreMerge := flag.Bool("im", false, "Ignore merge commit in changelog, default false")
	csvMode := flag.Bool("csv", false, "CSV changelog, default false")

	flag.Parse()

	log.Println("Github Releases Notes starts")

	compareInfo := &CompareInfo{
		Owner:       *githubOwner,
		Repo:        *githubRepo,
		Base:        *baseTag,
		Head:        *headTag,
		ignoreMerge: *ignoreMerge,
	}

	releaseInfo := GetReleaseInfo(compareInfo, githubToken)
	ExportChangelog(releaseInfo)
	if *csvMode {
		ExportChangelogCSV(releaseInfo)
	}
}
