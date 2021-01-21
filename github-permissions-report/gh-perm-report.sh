#!/usr/local/bin/bash

helpFunction()
{
   echo ""
   echo -e "Usage: $0 OWNER REPOSITORY [-t|--token TOKEN] \n\t\t\t[-a|--admin] [-w|--write] [-r|--read]\n"
   echo -e "\tOWNER\n\t\t Owner of the github repository."
   echo -e "\tREPOSITORY\n\t\t Github repository."
   echo -e "\t-t, --token <token>\n\t\t API token used to call github v3 api. Use \$GITHUB_TOKEN if not set."
   echo -e "\t-a, --admin\n\t\t Export Users with admin rights on the github repository."
   echo -e "\t-w, --write\n\t\t Export Users with push rights on the github repository."
   echo -e "\t-r, --read\n\t\t Export Users with pull rights on the github repository."
   exit 1 # Exit script after printing help
}

if [[ $# -lt 2 ]]; then
echo "There is at least one expected parameter empty";
helpFunction
fi;

POSITIONAL=()

owner=$1
repository=$2
shift # past owner
shift # past repository

while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -t|--token)
    GITHUB_TOKEN="$2"
    shift # past argument
    shift # past value
    ;;
    -a|--admin)
    admin='YES'
    shift # past argument
    ;;
    -w|--write)
    write='YES'
    shift # past argument
    ;;
    -r|--read)
    read='YES'
    shift # past argument
    ;;
    *)    # unknown option
    helpFunction
    ;;
esac
done

if [[ -z $GITHUB_TOKEN ]]; then
    echo "The GITHUB_TOKEN is need please refer to the doc"
    helpFunction
fi

echo "FETCH USERS for REPO $owner/$repository"

LAST_PAGE=$(curl -s -I -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$owner/$repository/collaborators?per_page=100&page=1" | grep Link: | sed 's/.*per_page=100&page=//g' | sed 's/>.*//g')

if [[ $admin == 'YES' ]]; then echo -n '' > admin.list; fi
if [[ $push == 'YES' ]]; then echo -n '' > push.list; fi
if [[ $pull == 'YES' ]]; then echo -n '' > pull.list; fi

for ((i=1; i<=LAST_PAGE; i++)); do
    curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$owner/$repository/collaborators?per_page=100&page=$i" > page-$i.json

    if [[ $admin == 'YES' ]]; then
        cat page-$i.json | jq -r ".[] | select(.permissions.admin==true) | .login" >> admin.list
    fi

    if [[ $push == 'YES' ]]; then
        cat page-$i.json | jq -r ".[] | select(.permissions.push==true) | .login" >> push.list
    fi

    if [[ $pull == 'YES' ]]; then
        cat page-$i.json | jq -r ".[] | select(.permissions.pull==true) | .login" >> pull.list
    fi
    rm -f page-$i.json
done

echo "# USERS for $owner/$repository" > "$repository.md"

if [[ $admin == 'YES' ]]; then

    echo "## ADMIN" >> "$repository.md"
    while read admin; do
        echo -n "* " >> "$repository.md"
        curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/users/$admin" | jq -r '[.name, .login] | join(" @")' >> "$repository.md"
    done <admin.list
    rm -f admin.list

fi

if [[ $push == 'YES' ]]; then

    echo "## WRITE" >> "$repository.md"
    while read push; do
        echo -n "* " >> "$repository.md"
        curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/users/$push" | jq -r '[.name, .login] | join(" @")' >> "$repository.md"
    done <push.list
    rm -f push.list

fi

if [[ $pull == 'YES' ]]; then

    echo "## READ" >> "$repository.md"
    while read pull; do
        echo -n "* " >> "$repository.md"
        curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/users/$pull" | jq -r '[.name, .login] | join(" @")' >> "$repository.md"
    done <pull.list
    rm -f pull.list

fi

cat "$repository.md"
