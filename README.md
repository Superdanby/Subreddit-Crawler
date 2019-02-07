# Subreddit-Crawler

## Environment Setup

1.	`sudo dnf install redhat-rpm-config python3-devel chromedriver`
2.	`python3 -m venv venv`
3.	`source venv/bin/activate`
4.	`pip install -r requirements.txt`
5.	`deactivate`

## Execution

1.	`./crawl.sh`

## Settings

In `Subreddit/crawl.sh`:
-	subreddit: name of subreddit
-	unix_time: an unix timestamp indicating when to stop
