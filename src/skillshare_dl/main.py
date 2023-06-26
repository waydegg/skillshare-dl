import json
import os
import re
from dataclasses import dataclass
from typing import Dict, List
from urllib.parse import urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup, Tag
from tqdm import tqdm


def save_json(data: Dict, filepath: str):
    with open(filepath, "w") as f:
        json.dump(data, f)


@dataclass
class Lesson:
    id: str
    unit_number: int
    lesson_number: int
    title: str


@dataclass
class Course:
    sku: int
    instructor_name: str
    course_name: str
    lessons: List[Lesson]


def clean_url(url):
    parsed_url = urlparse(url)
    match = re.search(r"\d+(?!.*\d)", parsed_url.path)
    if match:
        new_path = parsed_url.path[: match.end()]
    else:
        new_path = parsed_url.path
    cleaned_url = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            new_path,
            "",
            "",
            "",
        )
    )

    return cleaned_url


def get_course_data_from_url(url: str):
    cleaned_url = clean_url(url)

    res = httpx.get(
        url=cleaned_url,
        headers={
            "User-Agent": "Skillshare/5.3.0; Android 9.0.1",
        },
    )
    soup = BeautifulSoup(res.content, "html.parser")

    head_el = soup.head
    assert isinstance(head_el, Tag)
    script_el = head_el.find("script", string=re.compile("SS.serverBootstrap"))
    assert isinstance(script_el, Tag)
    script_match = re.search(
        r"SS\.serverBootstrap\s*=\s*(\{.*?\});", script_el.text, re.DOTALL
    )
    assert isinstance(script_match, re.Match)
    script_data = json.loads(script_match.group(1))

    lessons = []
    for unit_data in script_data["pageData"]["unitsData"]["units"]:
        unit_number = unit_data["rank"] + 1
        for session_data in unit_data["sessions"]:
            lesson = Lesson(
                id=session_data["id"],
                unit_number=unit_number,
                lesson_number=session_data["displayRank"],
                title=session_data["title"],
            )
            lessons.append(lesson)
    course = Course(
        sku=script_data["classData"]["sku"],
        instructor_name=script_data["classData"]["teacherName"],
        course_name=script_data["classData"]["parentClass"]["title"],
        lessons=lessons,
    )

    return course


def download_lesson(*, access_token: str, lesson: Lesson, download_path: str):
    url = f"https://api.skillshare.com/sessions/{lesson.id}/download"
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "x-locale": "en-US",
        "user-agent": "Skillshare/5.6.1 (iPhone; iOS 16.5.1)",
        "accept-language": "en-US,en;q=0.9",
        "authorization": f"Bearer {access_token}",
    }
    res = httpx.get(url=url, headers=headers, follow_redirects=True, timeout=30)
    res.raise_for_status()

    lesson_filename = f"{lesson.unit_number}.{lesson.lesson_number} - {lesson.title}"
    lesson_filepath = f"{download_path}/{lesson_filename}"
    lesson_filetype = "mp4"
    with open(f"{lesson_filepath}.{lesson_filetype}", "wb") as f:
        f.write(res.content)


def download_lesson_stream(*, access_token: str, lesson: Lesson, download_path: str):
    url = f"https://api.skillshare.com/sessions/{lesson.id}/download"
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "x-locale": "en-US",
        "user-agent": "Skillshare/5.6.1 (iPhone; iOS 16.5.1)",
        "accept-language": "en-US,en;q=0.9",
        "authorization": f"Bearer {access_token}",
    }

    lesson_filename = f"{lesson.unit_number}.{lesson.lesson_number} - {lesson.title}"
    lesson_filepath = f"{download_path}/{lesson_filename}"
    lesson_filetype = "mp4"
    with open(f"{lesson_filepath}.{lesson_filetype}", "wb") as f:
        with httpx.stream(
            "GET", url, headers=headers, follow_redirects=True
        ) as response:
            response.raise_for_status()
            total = int(response.headers["Content-Length"])
            with tqdm(
                total=total,
                unit_scale=True,
                unit_divisor=1024,
                unit="B",
                desc="Download Progress",
                leave=False,
            ) as progress:
                num_bytes_downloaded = response.num_bytes_downloaded
                for chunk in response.iter_bytes():
                    f.write(chunk)
                    progress.update(
                        response.num_bytes_downloaded - num_bytes_downloaded
                    )
                    num_bytes_downloaded = response.num_bytes_downloaded


def download(*, url: str, access_token: str, download_dir: str = "."):
    course_data = get_course_data_from_url(url)

    download_path = os.path.join(
        download_dir, f"./data/{course_data.instructor_name}/{course_data.course_name}"
    )

    # Make download path
    os.makedirs(download_path, exist_ok=True)

    for lesson in tqdm(course_data.lessons, desc="Lessons Downloaded"):
        download_lesson_stream(
            access_token=access_token,
            lesson=lesson,
            download_path=download_path,
        )
