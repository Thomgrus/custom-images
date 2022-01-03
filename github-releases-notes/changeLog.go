package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"

	"github.com/atsushinee/go-markdown-generator/doc"
)

func ExportChangelog(releaseInfo *ReleaseInfo) {
	changeLog := doc.NewMarkDown()

	changeLog.WriteLevel1Title(fmt.Sprintf("%s (%s)", releaseInfo.Name, releaseInfo.Date.Format("02/01/2006"))).
		Writeln()

	for _, commitInfo := range releaseInfo.Commits {
		changeLog.Write("* ").Write(commitInfo.Date.Format("02/01/2006")).Write(" - ")
		changeLog.WriteLink(commitInfo.Title, commitInfo.Link)
		changeLog.Write(" / ").Write(commitInfo.AuthorName)
		if len(commitInfo.Author) > 0 {
			changeLog.Write(" @").Write(commitInfo.Author)
		}
		changeLog.Writeln()
	}

	err := changeLog.Export("CHANGELOG.md")
	if err != nil {
		log.Fatalf("Unable to write changelog file %v", err)
	}
}

func ExportChangelogCSV(releaseInfo *ReleaseInfo) {

	data := [][]string{
		{"Commit ID", "Dev", "Date", "Description"},
	}

	for _, commitInfo := range releaseInfo.Commits {
		dataRow := []string{}
		dataRow = append(dataRow, commitInfo.SHA)
		dataRow = append(dataRow, commitInfo.AuthorName)
		dataRow = append(dataRow, commitInfo.Date.Format("02/01/2006"))
		dataRow = append(dataRow, commitInfo.Title)
		data = append(data, dataRow)
	}

	csvFile, err := os.Create("CHANGELOG.csv")
	if err != nil {
		log.Fatalf("failed creating file: %s", err)
	}
	defer csvFile.Close()

	csvwriter := csv.NewWriter(csvFile)
	defer csvwriter.Flush()

	for _, dataRow := range data {
		_ = csvwriter.Write(dataRow)
	}

}
