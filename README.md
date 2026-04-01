# FindMeAJob

A small Python CLI tool that helps me go through job listings faster by using an LLM to estimate how well they match my experience.

## Why I built this

Reading job descriptions over and over gets tiring, especially when most of them are vague or overloaded with requirements.

I wanted something that could:
- search job postings
- compare them against my actual experience
- give me a quick “is this worth applying to?” signal

This is just meant to be a helper to save time and filter obvious mismatches.

## What it does

- Searches for recent job postings on Google from popular job boards
- Uses LLM to extract key information from each job post
- Uses a structured profile (JSON) with my experience, skills, and preferences
- Sends both to an LLM for evaluation
- Returns a simple assessment of fit, with reasoning

Example output might include:
- Fit score / recommendation
- Missing skills or gaps
- Why it thinks the role is (or isn’t) a good match

## How it works (high level)

1. Job postings are scraped
2. Gemini extracts (and infers if necessary) key information from job postings
3. Gemini performs and returns a structured evaluation of how well my profile matches with each job posting
4. Results are stored in a database

## Goals

- Reduce time spent reading irrelevant job posts
- Get a second opinion on whether I actually match a role
- Highlight gaps I might be overlooking

## Limitations

- Depends heavily on prompt quality
- LLMs can be inconsistent
- Not a replacement for actually reading the job post
- Relies on Gemini to extract or infer job posts information

## Future ideas

- Implement an actual web scraping tool to extract job post information (this is to avoid relying 100% on Gemini)
- Tracking applications and outcomes
- Add support for multiple LLMs to compare results and reduce cost

## Tech

- Python (CLI)
- JSON for profile representation
- SerpAPI for scraping job postings
- Gemini for data analysis and profile evaluation