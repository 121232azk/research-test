# Newsletter Automation SOP

## Objective
Create an automated newsletter pipeline that:
1. Takes a topic as input
2. Researches the topic using Perplexity API
3. Generates infographics using Google Gemini (Nano Banana)
4. Writes newsletter content based on research
5. Formats complete HTML newsletter
6. Sends via Gmail API
7. Provides local preview option

## Overview
This system follows the WAT framework:
- **Workflows**: Define the complete pipeline and workflow steps
- **Agents**: Coordinate the execution (this is your role)
- **Tools**: Execute specific tasks (Python scripts in `tools/`)

## Required Inputs

### Essential Inputs
- **Topic**: The main subject of the newsletter (required)
- **Perplexity API Key**: For research and content generation
- **Google Gemini API Key**: For image generation
- **Gmail Credentials**: OAuth2 client secrets and token file

### Optional Inputs
- **Newsletters Title**: Default: "AI Trends Newsletter"
- **Author Name**: Default: "AI Insights Team"
- **Email Signature**: Default professional signature
- **Subject Template**: Custom email subject format
- **Output Quality**: High/Medium/Low (default: high)

## Pipeline Stages

### Stage 1: Research
**Objective**: Gather comprehensive information about the topic
**Tool**: `tools/research_topic.py`
**Inputs**: Topic, optional system prompt
**Outputs**: Structured research summary with citations
**Error Handling**:
- Retry up to 3 times on API failure
- Fallback to cached research if available

### Stage 2: Image Generation  
**Objective**: Create visual content for the newsletter
**Tool**: `tools/generate_infographics.py`
**Inputs**: Research summary, optional style preferences
**Outputs**: Generated images saved to `.tmp/`
**Error Handling**:
- Retry on rate limit errors
- Use text-based fallback if image generation fails
- Monitor API costs (Nano Banana is expensive)

### Stage 3: Content Writing
**Objective**: Generate HTML newsletter from research
**Tool**: `tools/write_content.py`
**Inputs**: Research results, image results, topic
**Outputs**: Complete HTML newsletter
**Error Handling**:
- Validate HTML structure
- Retry content generation if malformed
- Fallback to template-based content

### Stage 4: HTML Formatting
**Objective**: Finalize and optimize HTML newsletter
**Tool**: `tools/format_html.py`
**Inputs**: HTML content, image results, metadata
**Outputs**: Final formatted HTML
**Error Handling**:
- Validate HTML syntax
- Handle image optimization errors
- Ensure responsive design

### Stage 5: Email Sending
**Objective**: Deliver newsletter to recipients
**Tool**: `tools/send_email.py`
**Inputs**: Formatted HTML, recipients list
**Outputs**: Sent emails with tracking
**Error Handling**:
- OAuth2 token refresh
- Rate limiting for bulk sends
- Retry failed deliveries

### Stage 6: Local Preview
**Objective**: Preview newsletter before sending
**Tool**: `tools/dev_server.py`
**Inputs**: Formatted HTML
**Outputs**: Local web server with preview
**Error Handling**:
- Port availability
- File serving issues
- Browser compatibility

## Configuration Files

### `.env` File
```
# Required API Keys
PERPLEXITY_API_KEY=your_perplexity_api_key
GOOGLE_API_KEY=your_gemini_api_key

# Gmail Configuration
GMAIL_CREDENTIALS_FILE=./credentials.json
TOKEN_FILE=./token.json
NEWSLETTER_RECIPIENTS=email1@domain.com,email2@domain.com

# Optional Settings
NEWSLETTER_TITLE=AI Trends Newsletter
NEWSLETTER_SENDER_NAME=AI Insights Team
NEWSLETTER_SENDER_EMAIL=newsletter@youremail.com
NEWSLETTER_SIGNATURE=Best regards,\nAI Insights Team
NEWSLETTER_SUBJECT_TEMPLATE=AI Newsletter: {{topic}} - {{date}}

# Tool Settings
OUTPUT_QUALITY=high
OPTIMIZE_IMAGES=true
MAX_IMAGE_SIZE=500000
NEWSLETTER_TEMPLATE_PATH=./templates/newsletter.html
```

### `credentials.json`
Google OAuth2 client secrets (gitignored):
```json
{
  "installed": {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "redirect_uris": ["http://localhost:8080"]
  }
}
```

## Error Handling Strategy

### API Errors
1. **Rate Limits**: Implement exponential backoff (1s, 2s, 4s...)
2. **Authentication Failures**: Refresh OAuth2 tokens
3. **API Downtime**: Fallback to cached or template content
4. **Cost Issues**: Monitor Gemini usage, use Flash Lite for text-only

### Data Errors
1. **Invalid Input**: Validate before API calls
2. **Malformed Output**: Sanitize and retry
3. **File System Errors**: Use fallback locations, log issues

### Network Errors
1. **Connection Issues**: Retry with delays
2. **Timeouts**: Increase timeout values
3. **Proxy Issues**: Use system defaults

## Cost Considerations

### Perplexity API
- Usage-based pricing
- Monitor API calls
- Consider batch operations

### Google Gemini
- **Nano Banana 2**: $60/output token (expensive!)
- **Flash Lite**: $30/output token (recommended for text)
- Implement cost limits
- Use text-based content for cost efficiency

### Gmail API
- Free for sending
- Rate limits apply
- Monitor bulk send performance

## Local Development

### Running Dev Server
```bash
python tools/dev_server.py
```

### Workflow Execution
```bash
python tools/research_topic.py "topic" [system_prompt] [max_tokens]
python tools/generate_infographics.py "prompt" [model]
python tools/write_content.py ./tmp/research_topic.json ./tmp/newsletter.html "topic"
python tools/format_html.py newsletter.html ./tmp/images.json formatted_newsletter.html
python tools/send_email.py newsletter.html recipients.txt
```

### Manual Testing
1. Test each tool individually
2. Verify API keys work
3. Check file paths and permissions
4. Test error handling scenarios
5. Validate HTML output

## Success Metrics

### Quality Metrics
- Research citations: >3 sources per newsletter
- Image generation success: >80%
- HTML validation: W3C compliant
- Email deliverability: >95%
- Preview functionality: responsive and functional

### Performance Metrics
- Total pipeline time: <5 minutes
- API rate limit compliance: No throttling
- Memory usage: <500MB
- Error recovery: Automatic retry

### Operational Metrics
- Recipients per run: Configurable
- Daily email limits: Respected
- Cost per newsletter: <$1 (including Gemini)
- System uptime: >99%

## Automation Steps

### Manual Execution (for testing)
1. Set up `.env` with API keys
2. Run research tool
3. Run image generation tool
4. Run content writing tool
5. Run HTML formatting tool
6. Test with dev server
7. Send email

### Automated Execution (cron)
```bash
# Daily at 9 AM
0 9 * * * cd /path/to/newsletter && python3 tools/research_topic.py "topic" > research.log 2>&1 && python3 tools/generate_infographics.py "research results" >> images.log 2>&1 && ...
```

### Production Considerations
- Use proper logging
- Monitor API costs
- Implement monitoring and alerting
- Regular credential rotation
- Backup and disaster recovery

## Monitoring and Logging

### Log Files
- `research.log`: Research API calls and results
- `images.log`: Image generation attempts and costs
- `content.log`: Content generation and formatting
- `email.log`: Email sending and delivery tracking
- `server.log`: Dev server activity

### Monitoring Points
- API key validity
- Rate limit compliance
- Cost tracking
- Error frequency
- Success rates
- Delivery confirmations

## Security Considerations

### API Key Protection
- Store in `.env` (not in code)
- Use gitignore for credentials
- Implement key rotation
- Monitor key usage

### Gmail Security
- Use OAuth2 (never store passwords)
- Implement rate limiting
- Validate recipients
- Log send attempts

### Data Security
- Sanitize all inputs
- Validate HTML output
- Use HTTPS where possible
- Implement access controls

## Future Enhancements

### Planned Features
1. **Template System**: Custom newsletter templates
2. **A/B Testing**: Subject line and content variations
3. **Analytics**: Open rates, click-through rates
4. **Segmentation**: Different content for different audiences
5. **Scheduling**: Automated timing based on audience behavior
6. **Multi-channel**: SMS, social media integration

### Technical Improvements
1. **Caching**: Cache research results to reduce API calls
2. **Queue System**: Background processing for large batches
3. **Error Recovery**: Intelligent error handling and fallback
4. **Performance**: Optimize API calls and image processing
5. **Scalability**: Support for enterprise newsletter volumes

## Troubleshooting Guide

### Common Issues and Solutions

**Perplexity API Key Error**
- Check `.env` file has PERPLEXITY_API_KEY
- Verify API key is valid and not expired
- Ensure internet connection

**Gemini API Error**
- Check GOOGLE_API_KEY in `.env`
- Monitor costs (Nano Banana is expensive)
- Consider using Flash Lite for text-only content

**Gmail OAuth2 Error**
- Run `python tools/send_email.py` once to start OAuth2 flow
- Ensure credentials.json exists in correct location
- Check redirect URI in OAuth2 setup

**HTML Generation Error**
- Check template files in `./templates/`
- Validate HTML structure
- Ensure proper file permissions

**Dev Server Error**
- Check if port 8000 is available
- Verify file paths are correct
- Check Python dependencies

This SOP provides a comprehensive framework for building and maintaining an automated newsletter system. Follow the pipeline stages, implement proper error handling, and monitor costs and performance throughout the lifecycle.