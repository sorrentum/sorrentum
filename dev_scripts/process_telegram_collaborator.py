import argparse
import logging
import os

import requests

import helpers.hdbg as hdbg
import helpers.hparser as hparser

bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
_LOG = logging.getLogger(__name__)
_TELEGRAM_API = "https://api.telegram.org/bot"


def _get_invite_link(group_id: str) -> str:
    """
    Create a invite link of the Telegram group.
    """
    # Get group invite link.
    response = requests.get(
        f"{_TELEGRAM_API}{bot_token}/exportChatInviteLink?chat_id={group_id}",
        timeout=10,
    )
    status_code = response.status_code
    if status_code == 200:
        invite_link = response.json().get("result")
        return invite_link
    else:
        _LOG.debug(
            "Error retrieving permission level for %s. Status code: %s",
            group_id,
            status_code,
        )
    return None


def _invite_collaborator(user_id: str, group_id: str) -> None:
    """
    Invite a user to a Telegram group.
    """
    link = _get_invite_link(group_id)
    hdbg.dassert_is_not(link, None)
    text = f"Click this link to join the group: {link}"
    # Send a DELETE request to remove the collaborator.
    response = requests.get(
        f"{_TELEGRAM_API}{bot_token}/sendMessage",
        params={"chat_id": user_id, "text": text},
        timeout=10,
    )
    # Process response status code.
    status_code = response.status_code
    if status_code == 200:
        _LOG.debug("Invitation sent to user %s", user_id)
    elif status_code == 400:
        _LOG.debug("Bad request. User or chat ID might be incorrect.")
    else:
        _LOG.debug(
            "Error sending invitation to user %s. Status code: %s",
            user_id,
            status_code,
        )


def _remove_collaborator(user_id: str, group_id: str) -> None:
    """
    Remove a member from Telegram.
    """
    # Send a DELETE request to remove the collaborator.
    response = requests.get(
        f"{_TELEGRAM_API}{bot_token}/kickChatMember",
        params={"chat_id": group_id, "user_id": user_id},
        timeout=10,
    )
    # Process response status code.
    status_code = response.status_code
    if status_code == 204:
        _LOG.debug("%s has been removed from group.", user_id)
    elif status_code == 404:
        _LOG.debug("%s is not a group member.", user_id)
    else:
        _LOG.debug(
            "Error removing %s as a user. Status code: %s",
            user_id,
            status_code,
        )


def _get_group_info() -> None:
    """
    Get group id from Telegram.
    """
    response = requests.get(f"{_TELEGRAM_API}{bot_token}/getUpdates", timeout=10,)
    status_code = response.status_code
    if status_code == 200: 
        data = response.json()
        group_messages = {}
        for update in data["result"]:
            if "message" in update and "chat" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                message = update["message"]
                # Get the last message.
                if "text" in message:
                    group_messages[chat_id] = message["text"]
        for group_id, last_message in group_messages.items():
            print(f"Group ID: {group_id}, Last Message: {last_message}")
    else:
        _LOG.debug(
            "Error get group id. Status code: %s",
            status_code,
        )


def _parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--action",
        type=str,
        choices=["add", "remove", "get"],
        required=True,
        help="Action to perform: add or remove",
    )
    parser.add_argument(
        "--username", type=str, required=False, help="Username of the user"
    )
    parser.add_argument(
        "--groupid",
        type=str,
        required=False,
        help="Id of the group to add to",
    )
    hparser.add_verbosity_arg(parser)
    return parser


def _main(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()
    action = args.action
    username = args.username
    groupid = args.groupid
    hdbg.init_logger(verbosity=args.log_level, use_exec_path=True)
    if action == "add":
        hdbg.dassert_is_not(username, None)
        hdbg.dassert_is_not(groupid, None)
        _invite_collaborator(username, groupid)
    elif action == "remove":
        hdbg.dassert_is_not(username, None)
        hdbg.dassert_is_not(groupid, None)
        _remove_collaborator(username, groupid)
    elif action == "get":
        _get_group_info()
    else:
        raise ValueError("Invalid action ='%s'" % action)


if __name__ == "__main__":
    _main(_parse())