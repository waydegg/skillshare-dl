# skillshare-dl

A cli tool for downloading Skillshare lesson videos.

## Install

Install with [pipx](https://pypa.github.io/pipx/).

```bash
pipx install skillshare-dl
```

## Usage

1. Log into your Skillshare account.

You'll need an active Skillshare account to download lesson videos. As of June 2023,
Skillshare offers a 1-month free trial to new users.

2. Go to the course homepage that you want to download lesson videos for.

For example,
[here is the homepage](https://www.skillshare.com/en/classes/Motion-Graphics-with-Kurzgesagt-%E2%80%93-Part-1/631970755/projects?via=Selected-SearchSuggestion)
for Kurzgesagt's Motion Graphics course.

3. Get your access token.

Open your browser's Developer Tools and navigate to the browser storage tab. Find where
cookies for "https://www.skillshare.com" are stored and find the cookie "access_token".

4. Download the lesson videos.

Use the url of the course homepage and your access token with the `skillshare-dl` CLI
tool.

```bash
skillshare-dl \
  "[your-course-url]" \
  "[your-access-token]"
```

A complete example of this can look like:

```bash
skillshare-dl \
  "https://www.skillshare.com/en/classes/Motion-Graphics-with-Kurzgesagt-%E2%80%93-Part-1/631970755/projects?via=Selected-SearchSuggestion" \
  "eyJhbGciOi98y1yCho98y112Cl8Ga21dac3usImtpZCI6IldC..."
```

If you're getting 401 errors, refresh the page and use the new access token that was
generated.
