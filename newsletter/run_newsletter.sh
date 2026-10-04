#!/bin/bash
# Newsletter Automation Script
# Execute this script to run the complete newsletter pipeline

# Exit on any error
set -e

# Load environment variables - handle Windows line endings
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | tr '\r' '' | xargs)
else
    echo "❌ .env file not found!"
    echo "Please create .env file from .env.example"
    exit 1
fi

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Check if topic is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <topic>"
    echo "Example: $0 \"AI automation trends\""
    echo ""
    echo "This script runs the complete newsletter pipeline:"
    echo "1. Research topic using Perplexity API"
    echo "2. Generate infographic images"
    echo "3. Write newsletter content"
    echo "4. Format HTML newsletter"
    echo "5. Send via Gmail API (if configured)"
    echo ""
    echo "Options:"
    echo "  --preview    Start local development server for preview"
    echo "  --dry-run    Run pipeline but don't send email"
    echo ""
    exit 1
fi

TOPIC="\"$1\""
DRY_RUN=false
PREVIEW=false

# Parse options
while [[ $# -gt 1 ]]; do
    case $2 in
        --dry-run)
            DRY_RUN=true
            shift 2
            ;;
        --preview)
            PREVIEW=true
            shift 2
            ;;
        *)
            shift 2
            ;;
    esac
done

# Validate API keys
if [ -z "$PERPLEXITY_API_KEY" ]; then
    echo "❌ PERPLEXITY_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ GOOGLE_API_KEY not set in .env file"
    exit 1
fi

log "Starting newsletter automation pipeline..."
log "Topic: $TOPIC"

# Create timestamp for files
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
RUN_ID="newsletter_run_${TIMESTAMP}"
log "Run ID: $RUN_ID"

# Create temporary directory
TMP_DIR="./tmp"
mkdir -p "$TMP_DIR"

# Start time tracking
START_TIME=$(date +%s)

# Stage 1: Research
log "🚀 Stage 1: Research topic using Perplexity API"
RESEARCH_FILE="$TMP_DIR/research_${RUN_ID}.json"

echo "Researching: $TOPIC"
python tools/research_topic.py "$TOPIC" "Focus on comprehensive research for newsletter content" 1000 > "$RESEARCH_FILE"

if [ $? -eq 0 ]; then
    log "✅ Research completed successfully"
    log "📄 Results saved to: $RESEARCH_FILE"
else
    echo "❌ Research stage failed"
    exit 1
fi

# Stage 2: Image Generation
log "🚀 Stage 2: Generate infographic images using Google Gemini"
IMAGE_FILE="$TMP_DIR/images_${RUN_ID}.json"

echo "Generating images for: $TOPIC"
python tools/generate_infographics.py "Create newsletter visuals about: $TOPIC" gemini-3.1-flash-image > "$IMAGE_FILE"

if [ $? -eq 0 ]; then
    log "✅ Image generation completed successfully"
    log "📄 Results saved to: $IMAGE_FILE"
else
    echo "⚠️ Image generation failed, continuing with text-only content"
    echo "[]" > "$IMAGE_FILE"
fi

# Stage 3: Content Writing
log "🚀 Stage 3: Write newsletter content"
CONTENT_FILE="$TMP_DIR/content_${RUN_ID}.json"

echo "Writing content from research results..."
python tools/write_content.py "$RESEARCH_FILE" "$IMAGE_FILE" "$TOPIC" > "$CONTENT_FILE"

if [ $? -eq 0 ]; then
    log "✅ Content writing completed successfully"
    log "📄 Results saved to: $CONTENT_FILE"
else
    echo "❌ Content writing stage failed"
    exit 1
fi

# Stage 4: HTML Formatting
log "🚀 Stage 4: Format HTML newsletter"
NEWSLETTER_FILE="$TMP_DIR/newsletter_${RUN_ID}.html"

echo "Formatting HTML newsletter..."
python tools/format_html.py "$CONTENT_FILE" "$IMAGE_FILE" "$NEWSLETTER_FILE"

if [ $? -eq 0 ]; then
    log "✅ HTML formatting completed successfully"
    log "📄 Newsletter saved to: $NEWSLETTER_FILE"
else
    echo "❌ HTML formatting stage failed"
    exit 1
fi

# Stage 5: Preview (if requested)
if [ "$PREVIEW" = true ]; then
    log "🚀 Stage 5: Starting local preview server"
    echo "Starting development server on http://localhost:8000"
    echo "Press Ctrl+C to stop"
    python tools/dev_server.py
    log "✅ Preview server stopped"
    exit 0
fi

# Stage 6: Email Sending (unless dry run)
if [ "$DRY_RUN" = true ]; then
    log "🧪 DRY RUN: Skipping email sending"
    log "📄 Newsletter generated at: $NEWSLETTER_FILE"
else
    # Check if Gmail is configured
    if [ ! -f "credentials.json" ]; then
        echo "⚠️ Gmail credentials not found (credentials.json)"
        echo "Skipping email sending. Configure Gmail API to enable this feature."
        log "📄 Newsletter ready for sending: $NEWSLETTER_FILE"
    else
        log "🚀 Stage 5: Send newsletter via Gmail API"

        # Use default recipients from .env or command line
        if [ ! -z "$NEWSLETTER_RECIPIENTS" ]; then
            RECIPIENTS_FILE="$TMP_DIR/recipients_${RUN_ID}.txt"
            echo "$NEWSLETTER_RECIPIENTS" > "$RECIPIENTS_FILE"
            echo "Using recipients from .env: $RECIPIENTS_FILE"
        else
            echo "Enter recipient emails (comma-separated):"
            read -r RECIPIENTS
            RECIPIENTS_FILE="$TMP_DIR/recipients_${RUN_ID}.txt"
            echo "$RECIPIENTS" > "$RECIPIENTS_FILE"
        fi

        # Send newsletter
        echo "Sending newsletter to recipients..."
        python tools/send_email.py "$NEWSLETTER_FILE" "$RECIPIENTS_FILE"

        if [ $? -eq 0 ]; then
            log "✅ Newsletter sent successfully!"
        else
            echo "❌ Email sending failed"
            echo "📄 Newsletter saved locally: $NEWSLETTER_FILE"
        fi
    fi
fi

# End time tracking
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

log "🎉 Newsletter automation pipeline completed!"
log "⏱️  Total time: ${DURATION} seconds"
log "📁 Output directory: $TMP_DIR"
log "📄 Latest newsletter: $NEWSLETTER_FILE"

# List generated files
log "📋 Generated files:"
for file in "$TMP_DIR"/newsletter_${RUN_ID}*.html "$TMP_DIR"/research_${RUN_ID}.json "$TMP_DIR"/images_${RUN_ID}.json "$TMP_DIR"/recipients_${RUN_ID}.txt 2>/dev/null; do
    if [ -f "$file" ]; then
        echo "   $file"
    fi
done

# Clean up (optional)
# Uncomment the following line to automatically clean up temporary files
# rm -f "$TMP_DIR"/newsletter_${RUN_ID}*.html "$TMP_DIR"/research_${RUN_ID}.json "$TMP_DIR"/images_${RUN_ID}.json "$TMP_DIR"/recipients_${RUN_ID}.txt

echo ""
echo "✨ Newsletter automation completed successfully!"
echo ""
echo "To run this again with a different topic:"
echo "  $0 <topic>"
echo ""
echo "To preview the newsletter locally:"
echo "  $0 --preview <topic>"
echo ""
echo "To run in dry-run mode (no email sending):"
echo "  $0 --dry-run <topic>"

exit 0