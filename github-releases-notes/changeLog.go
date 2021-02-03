package main

import (
	"fmt"
	"log"

	"github.com/atsushinee/go-markdown-generator/doc"
)

func ExportChangelog(releaseInfo *ReleaseInfo) {
	changeLog := doc.NewMarkDown()

	changeLog.WriteLevel1Title(fmt.Sprintf("%s (%s)", releaseInfo.Name, releaseInfo.Date.Format("02/01/2006"))).
		Writeln()

	for _, commitInfo := range releaseInfo.Commits {
		changeLog.Write("* ").WriteLink(commitInfo.Title, commitInfo.Link).Write(" @").Write(commitInfo.Author).Writeln()
	}

	err := changeLog.Export("CHANGELOG.md")
	if err != nil {
		log.Fatalf("Unable to write changelog file %v", err)
	}
}
