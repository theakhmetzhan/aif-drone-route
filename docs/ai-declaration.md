# AI Use Declaration: Final Project, "Mini Drone Parcel Route"

Form: AIF1303 syllabus, Appendix to the Syllabus, "AI Use Declaration Form". AI drafted this declaration. Version 2, updated 2026-11-24 to cover the work for the final upload (repository, app, report, slides, video).

## Assignment

- **Assignment:** Final Project, "Mini Drone Parcel Route" (A\* search, Bayesian inference, MDP)
- **Course:** AIF1303 Artificial Intelligence Fundamentals, QAIRU, Fall 2026
- **Group:** Group 1
- **Student:** Akhmetzhan Turlybek (individual project)
- **AI-use level:** AI-3. The defence is AI-0.

## AI Tool

| Tool | Model and version | Date of use | Access mode |
| --- | --- | --- | --- |
| Claude (Anthropic), via Claude Code | Claude Opus 5.5 (`claude-opus-5-5`) | 2026-11-09, 2026-11-13, 2026-11-24 | Desktop app and agent sessions on my Mac; the model runs in Anthropic's cloud |
| Codex (OpenAI) | `gpt-6.2-sol` | 2026-11-24 | Agent sessions on my Mac; the model runs in OpenAI's cloud |
| ElevenLabs text-to-speech API | `eleven_v4`, voice "Zane - Calm, Suspenseful Storyteller" (`G4MBEL8urIiRY12lcDzS`) | 2026-11-24 | API called by a script that Claude Code ran, with a restricted text-to-speech-only key under a credit quota; 11 clips, 486 credits; runs in ElevenLabs' cloud |
| Whisper large-v3 (OpenAI model, MLX port) | `mlx-community/whisper-large-v3-mlx` | 2026-11-24 | Run locally on my Mac; transcribed the narration for a pronunciation check and timed the video's subtitle file (.srt) |

Non-AI tools: Python 3, Jupyter, Google Colab, matplotlib, ipywidgets, Streamlit, pytest, Git, GitHub, GitHub Actions, Google Chrome (PDF export). The video edit used ffmpeg and Playwright (non-AI tools). The demo video has narration only: no music and no sound effects.

## Purpose of Use

- **2026-11-09 and 2026-11-13:** topic proposal, code writing, testing, documentation (README) and defence preparation.
- **2026-11-24:** moving the notebook code into a public GitHub repository with tests and a Streamlit app; writing the technical report, the slides and presenter notes, the team contribution statement and this updated declaration; writing the demo video's narration script, generating the narration voice through the ElevenLabs API, transcribing it with Whisper to check pronunciation and time the subtitles, and editing the video; reviewing the code, its security, the slides and the documents.

## Key Prompts

1. "what topic do you propose, make it so that the entire thing is as easy as possible for me to learn for defence and actually defend myself orally."
2. (2026-11-24) "explain your plans for the repo, report, slides, statement, and video? use hq-design for design."
3. (2026-11-24) "all, parallelize as much as possible, use 6.2 sol high for review where relevant as well"

## AI Contribution

- **AI wrote (2026-11-09, 2026-11-13):** all notebook code (A\*, Bayes, MDP, tests, slider demo), the scenario's invented numbers, the README, the defence notes and the first version of this declaration.
- **Claude Opus 5.5 via Claude Code (2026-11-24):** built the GitHub repository (https://github.com/theakhmetzhan/aif-drone-route) with the notebook code moved unchanged into a Python package, the pytest test suite, the Streamlit app and the GitHub Actions workflow; wrote the technical report, the slides, the presenter notes, the team contribution statement and this updated declaration; wrote and ran the script that generated the narration through the ElevenLabs API; edited the demo video.
- **Codex, `gpt-6.2-sol` (2026-11-24):** wrote the narration script for the demo video, and reviewed the code, its security, the slides and the documents.
- **ElevenLabs `eleven_v4` (2026-11-24):** generated the narration audio (11 clips, 486 credits) with the voice "Zane - Calm, Suspenseful Storyteller". The video has no music and no sound effects.
- **Whisper large-v3, `mlx-community/whisper-large-v3-mlx` (2026-11-24), run locally:** transcribed the narration for a pronunciation check and timed the video's subtitle file (.srt).
- **Reused from the course:** the Bayes function and sensor numbers (0.30, 0.80, 0.20) follow Practical 6; A\* follows Week 2 and Assignment 1; the MDP step follows Practical 5 and the brief's implementation note.
- **My part:** choice of the topic among the proposals, the decision on the UI, the design direction for the final documents, text editing, verification (on 2026-11-24 I ran the test suite, clicked through the demo app, recomputed the key numbers on a calculator and skimmed the documents and slides; see My own verification), and preparing and giving the defence.

## Result Verification

### Checks run by the AI tools
- The notebook runs top to bottom without errors; 5 assert-based tests check the hand-calculated values (L = 10, b = 0.6316, Q(Fly) = −8.95, the no-alert case, a detour, a blocked goal).
- The A\* route length was compared with search without the heuristic on two maps.
- (2026-11-24) Every number in the technical report was recomputed by executing the notebook's own code cells. A separate script ran the notebook's functions on 200 random grids (seed 1303, 0 to 12 obstacles; 172 with a route, 28 without): on all 200, A\* and uniform-cost search agreed on the route length (or both found none), A\* expanded no more nodes, and the Manhattan heuristic never exceeded the true distance to the goal. The computed decision matched the break-even formula b\* = (22 − L) / (40 − L) at all 144,751 off-boundary points of the chart mesh, with zero mismatches (10 points on the boundary itself excluded).
- (2026-11-24) The repository's pytest suite runs in GitHub Actions with its own samplers (200 seeded grids with 0 to 14 obstacles, 60 grids for admissibility, posteriors summing to 1, the decision flip at b\*, exact-tie and near-tie tests, the zero-evidence guard, input validation). Codex reviewed the code, its security, the slides and the documents.

### My own verification
I ran the notebook in Google Colab with Run all and got the same numbers as the README. I checked the AI's calculations for b = 0.6316, Q(Fly) = −8.95 and the 0.40 break-even on a calculator and they matched. I tried the sliders.

(2026-11-24) I ran the repository's test suite (all 90 tests passed), started the Streamlit app on my Mac and clicked through the four scenarios (alert received: L = 10, b = 0.6316, Q(Fly) = −8.95, Wait; no alert: Fly; two long walls: L = 20, Fly; goal walled in: no route, Wait), recomputed b = 0.6316, Q(Fly) = −8.95 and the 0.40 break-even on a calculator, and skimmed the report, the slides and the other documents.

## Student Statement

I confirm that I am responsible for the final work and have disclosed AI use.

Signature: Akhmetzhan Turlybek

Date: 2026-11-24
