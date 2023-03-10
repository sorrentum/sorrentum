<!--ts-->
   * [Mailing lists](#mailing-lists)
   * [Organizing email flow](#organizing-email-flow)
   * [Anatomy of email messages from infra](#anatomy-of-email-messages-from-infra)
      * [Filtering emails with Gmail](#filtering-emails-with-gmail)
      * [Notifications from GitHub](#notifications-from-github)
      * [GitHub pull requests](#github-pull-requests)
         * [How to filter](#how-to-filter)
      * [GitHub issue activity](#github-issue-activity)
         * [How to filter](#how-to-filter-1)
      * [Commits](#commits)
         * [How to filter](#how-to-filter-2)
      * [Gdocs](#gdocs)
         * [How to filter](#how-to-filter-3)
      * [Jenkins](#jenkins)
         * [How to filter](#how-to-filter-4)
      * [TODO emails](#todo-emails)
         * [How to filter](#how-to-filter-5)



<!--te-->

# Mailing lists

- `all@` is the mailing list with everybody at the company

- We send notifications for commits and other services (e.g., Jenkins) to
  `git@`

- A GitHub user `infra` is used to check out code for services (e.g., Jenkins,
  ReviewBoard)

# Organizing email flow

- We receive tons of emails, and the inflow is going to keep increasing
  - At a large company you can get 10k emails per day (no kidding)

- The goal is to read _all_ the emails and always be on top of it

- How can one do that?
  - As usual the answer is get organized
  - Filter emails in folders

  1. Separate emails in folders based on the action that they require (e.g.,
     ignore, just read and be aware of it, read and respond)
  2. Read email and decide what to do about each of it:
     - No reply needed
     - Reply right away
     - Follow up later (e.g., to read, reply, think about it)
  3. Use flags to distinguish what needs to be followed up later or if you are
     waiting for a response

- A possible organization in folders is:
  - GitHub
    - Commits in all the repos (be aware of it)
    - Issue updates (read and respond)
    - PRs
    - Commits directly to `master` (read and review)
    - Commits into `documents` dir of `master` (read and review)
    - Emails generated by my GH activities (ignore and mark as read)
  - Jenkins
    - Breaks
    - All-is-good
  - Gdocs changes

# Anatomy of email messages from infra

- The goal is to classify emails so that we can filter email effectively

## Filtering emails with Gmail

- Personally (GP) I prefer an email client (Mozilla Thunderbird and more
  recently Apple Mail) rather than using Gmail web interface
  - People are able to use it

- Personally I prefer to use filters on the Gmail (server) side
  - Pros
    - I don't get emails on my cellphone continuously
    - The emails are organized as they arrive
    - Folders are on the server side, so my client can simply sync
  - Cons
    - The Gmail interface for filtering emails is horrible

- The web interface is `https://mail.google.com/mail/u/0/#settings/filters`

- Note that Gmail distinguish different email accounts using different indices,
  e.g., `https://mail.google.com/mail/u/<INDEX>/#inbox`

## Notifications from GitHub

- [https://help.github.com/en/categories/receiving-notifications-about-activity-on-github]

## GitHub pull requests

- These emails look like:
  ```
  Paul <notifications@github.com>
  Fri, Oct 11, 8:49 PM (22 hours ago)
  to
      alphamatic/amp (amp@noreply.github.com)
      Subscribed (subscribed@noreply.github.com)

  You can view, comment on, or merge this pull request online at:
    https://github.com/alphamatic/amp/pull/31

  Commit Summary
  PTask403: Add docstrings and type annotations
  Make comments self-consistent
  Add more docstrings, annotations
  ```

### How to filter

- These emails have `review_requested@noreply.github.com` in "to" field
- These emails have the words: "You can view, comment on, or merge this pull
  request online at:" in the body of the email

## GitHub issue activity

- These emails look like:
  ```
  GP Saggese <notifications@github.com>
  to
      .../... (...@noreply.github.com),
      me (...@gmail.com)
      Your (your_activity@noreply.github.com)

  A TOC (table of contents) for our md documentation might help navigating it,
  since it's not easy to have a view of the high level structure.

  A solution that seems pretty simple is here

  https://github.com/ekalinin/github-markdown-toc

  You are receiving this because you are subscribed to this thread.
  Reply to this email directly, view it on GitHub, or unsubscribe.
  ```

- Another email looks like:
  ```
  To: GP Saggese <notifications@github.com>
  Suject: [.../...] BUG: jupytext sync doesn't work anymore (#572)
  To: .../... <...@noreply.github.com>
  Cc:
      Giacinto Paolo Saggese <abc@xyz.com>,
      Your activity <your_activity@noreply.github.com>

  > jupytext --sync --to py:percent research/PTask218_Large_price_movement_analysis_for_security.py
  [jupytext] Reading research/PTask218_Large_price_movement_analysis_for_security.py
  [jupytext] Warning: 'research/PTask218_Large_price_movement_analysis_for_security.py' is not a paired notebook

  You are receiving this because you are subscribed to this thread.
  Reply to this email directly, view it on GitHub, or unsubscribe.
  ```

### How to filter

- These emails have different email addresses in the "to" field depending on the
  event that caused them:
  - `subscribed@noreply.github.com`: general GH bug activity (e.g., when the
    issue is opened)
  - `your_activity@noreply.github.com`: your GH bug activity
    - This is useful to recognize emails created by you and so automatically
      mark them as read
  - `comment@noreply.github.com`: comment on GH bug not from you

- These emails can be recognized by the fact that have the words "You are
  receiving this because you are subscribed to this thread." in the body

## Commits

- These emails look like:
  ```
  Sergey Malanin <noreply@github.com>
  to git

    Branch: refs/heads/master
    Home:   https://github.com/.../...
    Commit: b0431274fdf619cdb831e1274cd01841fe810b62
        https://github.com/.../.../commit/b0431274fdf619cdb831e1274cd01841fe810b62
    Date:   2019-10-12 (Sat, 12 Oct 2019)

    Changed paths:
      M Data_encyclopedia.ipynb
      M Data_encyclopedia.py

    Log Message:
    -----------
    PTask302 added reader in DE
  ```

### How to filter

- These emails come from `notifications@github.com`
- These emails can be recognized by the fact that have the words "Changed
  paths:" in the email body

## Gdocs

### How to filter

- These emails have `comments-noreply@docs.google.com` or `(Google Docs)` in the
  "subject" field

## TODO emails

### How to filter

- These emails have `TODO` in the subject
