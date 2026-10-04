# Agent Instructions

You're working inside the **WAT framework** (Workflows, Agents, Tools). This architecture separates concerns so that probabilistic AI handles reasoning while deterministic code handles execution. That separation is what makes this system reliable.

## The WAT Architecture

**Layer 1: Workflows (The Instructions)**
- Markdown SOPs stored in `workflows/`
- Each workflow defines the objective, required inputs, which tools to use, expected outputs, and how to handle edge cases
- Written in plain language, the same way you'd brief someone on your team

**Layer 2: Agents (The Decision-Maker)**
- This is your role. You're responsible for intelligent coordination.
- Read the relevant workflow, run tools in the correct sequence, handle failures gracefully, and ask clarifying questions when needed
- You connect intent to execution without trying to do everything yourself
- Example: If you need to pull data from a website, don't attempt it directly. Read `workflows/scrape_website.md`, figure out the required inputs, then execute `tools/scrape_single_site.py`

**Layer 3: Tools (The Execution)**
- Python scripts in `tools/` that do the actual work
- API calls, data transformations, file operations, database queries
- Credentials and API keys are stored in `.env`
- These scripts are consistent, testable, and fast

**Why this matters:** When AI tries to handle every step directly, accuracy drops fast. If each step is 90% accurate, you're down to 59% success after just five steps. By offloading execution to deterministic scripts, you stay focused on orchestration and decision-making where you excel.

## How to Operate

**1. Look for existing tools first**
Before building anything new, check `tools/` based on what your workflow requires. Only create new scripts when nothing exists for that task.

**2. Learn and adapt when things fail**
When you hit an error:
- Read the full error message and trace
- Fix the script and retest (if it uses paid API calls or credits, check with me before running again)
- Document what you learned in the workflow (rate limits, timing quirks, unexpected behavior)
- Example: You get rate-limited on an API, so you dig into the docs, discover a batch endpoint, refactor the tool to use it, verify it works, then update the workflow so this never happens again

**3. Keep workflows current**
Workflows should evolve as you learn. When you find better methods, discover constraints, or encounter recurring issues, update the workflow. That said, don't create or overwrite workflows without asking unless I explicitly tell you to. These are your instructions and need to be preserved and refined, not tossed after one use.

## The Self-Improvement Loop

Every failure is a chance to make the system stronger:
1. Identify what broke
2. Fix the tool
3. Verify the fix works
4. Update the workflow with the new approach
5. Move on with a more robust system

This loop is how the framework improves over time.

## File Structure

**What goes where:**
- **Deliverables**: Final outputs go to cloud services (Google Sheets, Slides, etc.) where I can access them directly
- **Intermediates**: Temporary processing files that can be regenerated

**Directory layout:**
```
.tmp/           # Temporary files (scraped data, intermediate exports). Regenerated as needed.
tools/          # Python scripts for deterministic execution
workflows/      # Markdown SOPs defining what to do and how
.env            # API keys and environment variables (NEVER store secrets anywhere else)
credentials.json, token.json  # Google OAuth (gitignored)
```

**Core principle:** Local files are just for processing. Anything I need to see or use lives in cloud services. Everything in `.tmp/` is disposable.

## Bottom Line

You sit between what I want (workflows) and what actually gets done (tools). Your job is to read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system as you go.

Stay pragmatic. Stay reliable. Keep learning.

## Newsletter Automation System

This project implements a complete newsletter automation system using the WAT framework. Here's what you need to know:

### Key Features

- **Automated Research**: Uses Perplexity API to research topics
- **Visual Content**: Generates infographic images using Google Gemini (Nano Banana models)
- **Content Generation**: Creates professional HTML newsletters from research
- **Email Delivery**: Sends newsletters via Gmail API with OAuth2 authentication
- **Local Preview**: Development server for previewing before sending
- **Error Handling**: Comprehensive error handling and retry mechanisms
- **Cost Control**: Gemini API cost monitoring and optimization options

### Required Setup

1. **API Keys** (configured in `.env`):
   - Perplexity API key for research
   - Google Gemini API key for image generation

2. **Gmail Setup** (for email delivery):
   - Create Google Cloud project
   - Enable Gmail API
   - Create OAuth2 credentials (`credentials.json`)
   - Run `python tools/send_email.py` once for initial authentication

3. **Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Usage Examples

```bash
# Run complete newsletter pipeline for a topic
./run_newsletter.sh "Your topic here"

# Run in dry-run mode (generate but don't send)
./run_newsletter.sh --dry-run "Your topic here"

# Start local preview server
./run_newsletter.sh --preview "Your topic here"
```

### Quick Start

1. **Test individual tools**:
   ```bash
   python tools/research_topic.py "Sample topic"
   python tools/generate_infographics.py "Sample prompt"
   python tools/write_content.py ./tmp/research.json
   python tools/format_html.py newsletter.html ./tmp/images.json
   python tools/dev_server.py
   ```

2. **Complete workflow**:
   ```bash
   ./run_newsletter.sh "AI automation trends 2024"
   ```

### Output Files

Generated files are saved to `./tmp/`:
- `research_*.json` - Research results from Perplexity
- `images_*.json` - Generated image metadata
- `content_*.json` - Formatted newsletter content
- `newsletter_*.html` - Final HTML newsletter
- `recipients_*.txt` - Email recipient list (if sending)

### Monitoring and Troubleshooting

- **Local Preview**: `python tools/dev_server.py` for live preview
- **API Keys**: Check `.env` file for correct configuration
- **Error Logs**: Review `./tmp/` files for detailed error information
- **Gmail Setup**: Ensure OAuth2 authentication is completed

### Cost Considerations

- **Gemini API**: ~$60/output token for Nano Banana 2, consider using `gemini-3.1-flash-lite` for text-only content
- **Perplexity API**: Usage-based pricing
- **Gmail API**: Free for sending emails

### Future Enhancements

- Multi-channel distribution (SMS, social media)
- Analytics and tracking
- Template customization
- Scheduling and automation
- Multi-recipient segmentation

### Key Files

- **`tools/`** - Core processing scripts
- **`workflows/`** - Workflow SOP documentation  
- **`templates/`** - HTML email templates
- **`.env`** - Configuration and API keys
- **`run_newsletter.sh`** - Main execution script
- **`README.md`** - Complete documentation

This system provides a robust, automated solution for creating and delivering professional newsletters with minimal manual intervention.
