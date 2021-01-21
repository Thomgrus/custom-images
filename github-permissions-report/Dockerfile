FROM bash:5.1.4
RUN apk --no-cache add curl
COPY gh-perm-report.sh github-permissions-report
ENTRYPOINT ["./github-permissions-report"]
