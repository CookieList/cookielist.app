#!/bin/bash

CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

REPOSITORY=$1
if [ -z "$REPOSITORY" ]; then
    DEFAULT_REPOSITORY="CookieList/cookielist.test"
    echo -e -n "${CYAN}Enter CookieList Repository Name${NC} [${GREEN}$DEFAULT_REPOSITORY${NC}]: "
    read REPOSITORY
    if [ -z "$REPOSITORY" ]; then
        REPOSITORY="$DEFAULT_REPOSITORY"
    fi
fi

echo -e -n "${CYAN}Enter DotEnv Key${NC}: "
read DOTENV_KEY

if [[ -d . && -n "$(ls -A .)" ]]; then
    echo -e "${YELLOW}Warning:${NC} Current Directory Is Not Empty."
    echo -e -n "${CYAN}Empty '$(pwd)'${NC} [${GREEN}Yes/(No)${NC}]: "
    read CHOICE

    case $CHOICE in
    "YES" | "yes" | "Yes" | "Y" | "y")
        echo -e "${CYAN}Info:${NC} Clearing Curret Directory."
        find . -mindepth 1 -exec rm -rf -- {} +
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

git clone "https://github.com/$REPOSITORY.git" .

if [ $? -eq 0 ]; then
    echo -e "${CYAN}Info:${NC} Cloned Repository 'https://github.com/$REPOSITORY.git' At '$(pwd)'"

    if [ -f "requirements.txt" ]; then
        python -m pip install -r requirements.txt

        if [ $? -eq 0 ]; then
            echo -e "${CYAN}Info:${NC} Dependencies Installed Successfully."
        else
            echo -e "${RED}Error:${NC} Failed To Install Dependencies."
        fi
    else
        echo -e "${YELLOW}Warning:${NC} No requirements.txt Found In The Repository."
    fi

    if [ "$DOTENV_KEY" != "" ]; then
        echo -e "${CYAN}Info:${NC} Creating .dotenv.key"
        echo "$DOTENV_KEY" > .dotenv.key
    fi

    echo -e "${CYAN}Info:${NC} Removing .git"
    rm -rf .git

    echo -e "${GREEN}Success:${NC} Setup Completed Successfully."

else
    echo -e "${RED}Error:${NC} Failed To Clone The Repository."
fi
