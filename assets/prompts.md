# Prompts

## NotebookLM Prompts:
- Create a bibliography of all articles, videos, ... used in this podcast. You definitely need to use google search to do that. I want the list of references with the links.


## Cursor Prompts:
- @2-transcript.md is a Persian (Farsi) transcript of a podcast.
Make it more readible by merging the different related text blocks and removing unnecessary spaces and new lines.
More importantly, fix typos since this transcript has been generated with AI.

- @chista.ryanxai.com/source/Episode-02/3-transcript.md Translate all the text in a verbatim manner to Persian (Farsi).
You should figure out which sentence belongs to which speaker and add it to your translation.


## EslPal Prompt
```
</transcript>
{text}
</transcript>

<instructions>
You are an expert ESL teacher. Your job is helping an advanced ESL learner to improve their English. You are given the full transcript of a podcast , and your job is to help the learner to master the text by highlighting the words, idioms, and phrases used in the text alongside their definition matching the context. So, just focus on the words, idioms, and phrases in this level of English. Carefully scan the whole text, identify all words, idioms, and phrases used in the text alongside their definition matching the context and provide them using this syntax [highlighted text]{definition}.

You should also figure out which sentence belongs to which speaker and add it to your translation. Also, add the speaker's name to the beginning of the sentence.

Note that there might be some typos in podcast's transcript. So, fix them.

Don't remove any part of the transcript. Just augment it with highlights and definitions.
</instructions>
```
