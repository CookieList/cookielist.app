#!bash

# Bash script to setup a new CookieList project
#
# $1 == CookieList Repository Name (e.g. gh_username/repo_name)
# $2 == CookieList Project App Id (e.g. cookielist-core-or-stub-app)
# $3 == Empty Directory Warning (e.g. "Yes" or "No")
# $4 == DotEnv Key (e.g. dotenv://:key_dotenv_project_hash_id@dotenv.org/vault/.env.vault?environment=environment_id)

CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'
DIRECTORY=$(pwd)

echo -e "${CYAN}[${NC}${GREEN}CookieList${NC}${CYAN}] Project Setup Script.${NC}"

REPOSITORY=$1
if [ -z "$REPOSITORY" ]; then
    DEFAULT_REPOSITORY="CookieList/cookielist.test"
    echo -e -n "${CYAN}Enter CookieList Repository Name${NC} [${GREEN}$DEFAULT_REPOSITORY${NC}]: "
    read REPOSITORY
    if [ -z "$REPOSITORY" ]; then
        REPOSITORY="$DEFAULT_REPOSITORY"
    fi
fi

COOKIELIST_APP=$2
if [ -z "$COOKIELIST_APP" ]; then
    echo -e -n "${CYAN}Enter CookieList App Id${NC}: "
    read COOKIELIST_APP
fi

if [[ -d $DIRECTORY && -n "$(ls -A $DIRECTORY)" ]]; then
    CHOICE=$3
    if [ -z "$CHOICE" ]; then
        echo -e "${YELLOW}Warning:${NC} Current Directory Is Not Empty."
        echo -e -n "${CYAN}Empty '$DIRECTORY'${NC} [${GREEN}Yes/(No)${NC}]: "
        read CHOICE
    fi
    
    case $CHOICE in
        "YES" | "yes" | "Yes" | "Y" | "y")
            echo -e "${CYAN}Info:${NC} Clearing Curret Directory."
            find $DIRECTORY -mindepth 1 -exec rm -rf -- {} +
            if [ $? -eq 0 ]; then
                echo -e "${CYAN}Info:${NC} Curret Directory Cleared Successfully"
            else
                echo -e "${RED}Error:${NC} Directory Clearing Failed, Terminated Setup."
                exit 1
            fi
        ;;
        "NO" | "no" | "No" | "N" | "n")
            echo -e "${YELLOW}Warning:${NC} Repository Cloning Require Empty Directory."
            echo -e "${CYAN}Info:${NC} Exiting Setup."
            exit
        ;;
        *)
            echo -e "${RED}Error:${NC} Invalid Input, Terminated Setup."
            exit 1
        ;;
    esac
fi

DOTENV_KEY=$4
if [ -z "$DOTENV_KEY" ]; then
    echo -e -n "${CYAN}Enter DotEnv Key${NC}: "
    read DOTENV_KEY
fi

git clone "https://github.com/$REPOSITORY.git" $DIRECTORY

if [ $? -eq 0 ]; then
    echo -e "${CYAN}Info:${NC} Cloned Repository 'https://github.com/$REPOSITORY.git' At '$(pwd)'"
    
    if [ -f "$DIRECTORY/requirements.txt" ]; then
        python -m pip install -r $DIRECTORY/requirements.txt
        
        if [ $? -eq 0 ]; then
            echo -e "${CYAN}Info:${NC} Dependencies Installed Successfully."
        else
            echo -e "${RED}Error:${NC} Failed To Install Dependencies."
        fi
    else
        echo -e "${YELLOW}Warning:${NC} No requirements.txt Found In The Repository."
    fi
    
    echo -e "${CYAN}Info:${NC} Creating app.py"
    {
        echo "#!/usr/bin/env python"
        echo ""
        echo "# This file is part of the 'CookieList' project."
        echo "# automatically created by setup.sh on '$(date)'."
        echo "# with the github repository https://github.com/$REPOSITORY.git"
        echo ""
        echo "import os"
        echo "from cookielist.__main__ import get_app"
        echo ""
        echo "os.environ['DOTENV_KEY'] = '$DOTENV_KEY'"
        echo "app = get_app('$COOKIELIST_APP')"
        echo ""
    } > $DIRECTORY/app.py
    
    echo -e "${CYAN}Info:${NC} Removing .git"
    rm -rf $DIRECTORY/.git
    
    echo -e "${GREEN}Success:${NC} Setup Completed Successfully."
    
else
    echo -e "${RED}Error:${NC} Failed To Clone The Repository."
fi
