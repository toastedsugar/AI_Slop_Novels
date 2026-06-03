## Things to look out for.

Prompt caching 
Right now, I'm extracting character, location, object information and building a new prompt for each chapter. The costs for this are rather high. 
If I instead send the whole character, location and object context to the claude API as a system prompt and include the specific character, etc... information in the user prompt, I can use prompt caching to store the system prompt between each chapter generation. 

When a request begins with the same sequence of tokens as a previous request, the API reuses the previously processed representation rather than recomputing it. It operates on prefixes — the cached portion must appear at the beginning of the context, before the dynamic parts. 

But at at a certain scale, say a 100,000 word novel with 40 characters, 50 locations, and a massive continuity, the context window might not be large enough to handle it. I can do tiered caching. Keep the core characters and locations and stuff in the system prompt to be cached while supporting information can be provided in the user prompt.

Batch API will take longer but be much cheaper.








Locally create a prompt for a chapter using blueprint and continuity information
AI model generates prose and summary and what has changed in this chapter.
Add summary to running summary
Save changes to continuity file







