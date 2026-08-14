from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
from datetime import date
import re
import shutil
import os
import json
import base64
import urllib.request
import urllib.error
from urllib.parse import quote

app = Flask(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT_DIR / "_posts"
DRAFTS_DIR = ROOT_DIR / "cms" / "drafts"

POSTS_DIR.mkdir(exist_ok=True)
DRAFTS_DIR.mkdir(exist_ok=True)

GITHUB_OWNER = "natsumiqinghu-afk"
GITHUB_REPO = "koiuranai"
GITHUB_BRANCH = "main"


def make_filename(title, post_date):
    safe_title = re.sub(r'[\\/:*?"<>|]', "", title)
    safe_title = safe_title.strip().replace(" ", "-")
    return f"{post_date}-{safe_title}.md"


def make_list(value):
    items = [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]
    return "[" + ", ".join(items) + "]"


def create_markdown(
    title,
    post_date,
    category,
    age,
    tags,
    body,
    status="draft",
    publish_at=""
):
    return f"""---
layout: post
title: "{title}"
date: {post_date}
categories: {make_list(category)}
age: "{age}"
tags: {make_list(tags)}
status: "{status}"
publish_at: "{publish_at}"
---

{body}
"""


def upload_to_github(filepath):
    token = os.environ.get("GITHUB_TOKEN")

    if not token:
        raise Exception("GITHUB_TOKEN が設定されていません")

    relative_path = filepath.relative_to(ROOT_DIR)
    github_path = str(relative_path).replace("\\", "/")
    github_path = quote(github_path, safe="/")

    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/contents/{github_path}"
    )

    content = filepath.read_bytes()
    encoded_content = base64.b64encode(content).decode("utf-8")

    sha = None

    get_request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "mamamiya-cms"
        }
    )

    try:
        with urllib.request.urlopen(get_request) as response:
            existing = json.loads(
                response.read().decode("utf-8")
            )
            sha = existing.get("sha")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise

    data = {
        "message": f"CMS: {filepath.name}",
        "content": encoded_content,
        "branch": GITHUB_BRANCH
    }

    if sha:
        data["sha"] = sha

    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        method="PUT",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "mamamiya-cms",
            "Content-Type": "application/json"
        }
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def parse_post(filepath, status):
    text = filepath.read_text(encoding="utf-8")

    match = re.match(
        r"^---\s*\n(.*?)\n---\s*\n(.*)$",
        text,
        re.DOTALL
    )

    if not match:
        return {
            "filename": filepath.name,
            "title": filepath.stem,
            "date": "",
            "category": "",
            "age": "",
            "tags": "",
            "status": status,
            "publish_at": "",
            "body": text
        }

    front_matter = match.group(1)
    body = match.group(2).strip()

    def get_value(name):
        result = re.search(
            rf"^{name}:\s*(.*)$",
            front_matter,
            re.MULTILINE
        )
        return result.group(1).strip() if result else ""

    title = get_value("title").strip('"')
    post_date = get_value("date")
    category = get_value("categories")
    age = get_value("age").strip('"')
    tags = get_value("tags")
    publish_at = get_value("publish_at").strip('"')

    category = category.strip("[]").replace('"', "")
    tags = tags.strip("[]").replace('"', "")

    return {
        "filename": filepath.name,
        "title": title,
        "date": post_date,
        "category": category,
        "age": age,
        "tags": tags,
        "status": status,
        "publish_at": publish_at,
        "body": body
    }


@app.route("/")
def index():
    published_posts = []
    draft_posts = []
    scheduled_posts = []

    for filepath in POSTS_DIR.glob("*.md"):
        published_posts.append(
            parse_post(filepath, "published")
        )

    for filepath in DRAFTS_DIR.glob("*.md"):
        post = parse_post(filepath, "draft")

        if post["publish_at"]:
            post["status"] = "scheduled"
            scheduled_posts.append(post)
        else:
            draft_posts.append(post)

    published_posts.sort(
        key=lambda x: x["date"],
        reverse=True
    )

    draft_posts.sort(
        key=lambda x: x["date"],
        reverse=True
    )

    scheduled_posts.sort(
        key=lambda x: x["publish_at"]
    )

    return render_template(
        "index.html",
        posts=published_posts,
        drafts=draft_posts,
        scheduled=scheduled_posts
    )


@app.route("/new")
def new_post():
    return render_template(
        "editor.html",
        today=date.today().isoformat(),
        post=None,
        status="draft"
    )


@app.route("/edit/<status>/<path:filename>")
def edit_post(status, filename):
    if status == "draft":
        filepath = DRAFTS_DIR / filename
    elif status == "published":
        filepath = POSTS_DIR / filename
    elif status == "scheduled":
        filepath = DRAFTS_DIR / filename
    else:
        return "不正なステータスです", 400

    if not filepath.exists():
        return "記事が見つかりません", 404

    post = parse_post(filepath, status)

    return render_template(
        "editor.html",
        today=date.today().isoformat(),
        post=post,
        status=status
    )


def github_error_page(e):
    return f"""
    <h1>GitHub保存に失敗しました</h1>
    <p>{e}</p>
    <p><a href="/">CMSへ戻る</a></p>
    """, 500


@app.route("/create", methods=["POST"])
def create_post():
    title = request.form.get("title", "").strip()
    post_date = request.form.get("date", "").strip()
    category = request.form.get("category", "").strip()
    age = request.form.get("age", "").strip()
    tags = request.form.get("tags", "").strip()
    body = request.form.get("body", "").strip()
    publish_at = request.form.get("publish_at", "").strip()

    if not title:
        return "タイトルを入力してください", 400

    if not post_date:
        post_date = date.today().isoformat()

    status = "scheduled" if publish_at else "draft"

    markdown = create_markdown(
        title,
        post_date,
        category,
        age,
        tags,
        body,
        status=status,
        publish_at=publish_at
    )

    filename = make_filename(title, post_date)
    filepath = DRAFTS_DIR / filename

    filepath.write_text(
        markdown,
        encoding="utf-8"
    )

    try:
        upload_to_github(filepath)
    except Exception as e:
        return github_error_page(e)

    return redirect(url_for("index"))


@app.route("/update/draft/<path:filename>", methods=["POST"])
def update_draft(filename):
    return update_existing(
        filename,
        DRAFTS_DIR,
        "draft"
    )


@app.route("/update/scheduled/<path:filename>", methods=["POST"])
def update_scheduled(filename):
    return update_existing(
        filename,
        DRAFTS_DIR,
        "scheduled"
    )


@app.route("/update/published/<path:filename>", methods=["POST"])
def update_published(filename):
    return update_existing(
        filename,
        POSTS_DIR,
        "published"
    )


def update_existing(filename, directory, current_status):
    old_filepath = directory / filename

    if not old_filepath.exists():
        return "記事が見つかりません", 404

    title = request.form.get("title", "").strip()
    post_date = request.form.get("date", "").strip()
    category = request.form.get("category", "").strip()
    age = request.form.get("age", "").strip()
    tags = request.form.get("tags", "").strip()
    body = request.form.get("body", "").strip()
    publish_at = request.form.get("publish_at", "").strip()

    if not title:
        return "タイトルを入力してください", 400

    if not post_date:
        post_date = date.today().isoformat()

    if current_status == "published":
        status = "published"
    else:
        status = "scheduled" if publish_at else "draft"

    markdown = create_markdown(
        title,
        post_date,
        category,
        age,
        tags,
        body,
        status=status,
        publish_at=publish_at
    )

    new_filename = make_filename(title, post_date)
    new_filepath = directory / new_filename

    if old_filepath != new_filepath:
        old_filepath.unlink()

    new_filepath.write_text(
        markdown,
        encoding="utf-8"
    )

    try:
        upload_to_github(new_filepath)
    except Exception as e:
        return github_error_page(e)

    return redirect(url_for("index"))


@app.route(
    "/github-save/<status>/<path:filename>",
    methods=["POST"]
)
def github_save(status, filename):
    if status == "draft":
        filepath = DRAFTS_DIR / filename
    elif status == "scheduled":
        filepath = DRAFTS_DIR / filename
    elif status == "published":
        filepath = POSTS_DIR / filename
    else:
        return "不正なステータスです", 400

    if not filepath.exists():
        return "記事が見つかりません", 404

    try:
        upload_to_github(filepath)
    except Exception as e:
        return github_error_page(e)

    return redirect(url_for("index"))


@app.route(
    "/publish/<path:filename>",
    methods=["POST"]
)
def publish_post(filename):
    draft_filepath = DRAFTS_DIR / filename

    if not draft_filepath.exists():
        return "下書きが見つかりません", 404

    published_filepath = POSTS_DIR / filename

    if published_filepath.exists():
        return "同じ名前の記事がすでに公開されています", 400

    shutil.move(
        str(draft_filepath),
        str(published_filepath)
    )

    try:
        upload_to_github(published_filepath)
    except Exception as e:
        return github_error_page(e)

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
