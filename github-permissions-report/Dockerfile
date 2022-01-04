FROM bash:5
RUN apk --no-cache add curl jq
COPY gh-perm-report.sh /usr/local/bin/github-permissions-report
ENTRYPOINT ["github-permissions-report"]
