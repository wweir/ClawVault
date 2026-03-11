# ClawVault Examples

This directory contains example scripts and integrations for ClawVault.

## OpenClaw Skill: Rule Generator

**File:** `openclaw-skill-generate-rule.py`

Generate ClawVault security rules from natural language directly within OpenClaw.

### Installation

```bash
# Install dependencies
pip install requests pyyaml

# Make executable
chmod +x openclaw-skill-generate-rule.py
```

### Usage

**Basic usage:**
```bash
./openclaw-skill-generate-rule.py "Block all AWS credentials"
```

**Generate and apply immediately:**
```bash
./openclaw-skill-generate-rule.py "Auto-sanitize PII data" --apply
```

**Generate multiple rules:**
```bash
./openclaw-skill-generate-rule.py "Tiered security: block high-risk, sanitize medium-risk" --multiple
```

**Use remote ClawVault instance:**
```bash
./openclaw-skill-generate-rule.py "Block prompt injections" --url http://<server-ip>:8766
```

**JSON output for scripting:**
```bash
./openclaw-skill-generate-rule.py "Block dangerous commands" --json | jq '.rules'
```

### Common Policies

**Security:**
- "Block all prompt injection attempts"
- "Block all AWS credentials"
- "Block dangerous shell commands"

**Data Protection:**
- "Auto-sanitize Chinese ID cards, phone numbers, and emails"
- "Sanitize all API keys with risk score above 7.0"
- "Block credit card numbers and crypto private keys"

**Environment-Specific:**
- "In development, log all detections but allow everything except injections"
- "In production, block all threats with risk score above 8.0"
- "For customer service, auto-sanitize PII data"

### Integration with OpenClaw

**Option 1: Direct execution**
```bash
# From OpenClaw terminal
python /path/to/openclaw-skill-generate-rule.py "Your policy"
```

**Option 2: OpenClaw Skill**
```bash
# Copy to OpenClaw skills directory
cp openclaw-skill-generate-rule.py ~/.openclaw/skills/

# Run from OpenClaw
openclaw skill run generate-rule "Block all AWS credentials"
```

**Option 3: API integration**
```python
import requests

response = requests.post(
    "http://localhost:8766/api/rules/generate",
    json={"policy": "Block all AWS credentials"}
)

if response.json()["success"]:
    rules = response.json()["rules"]
    print(f"Generated {len(rules)} rules")
```

### Examples

**Example 1: Customer Service Agent**
```bash
./openclaw-skill-generate-rule.py \
  "For customer service, auto-sanitize Chinese ID cards, phone numbers, and email addresses" \
  --apply
```

**Output:**
```yaml
- id: customer-service-pii-sanitize
  name: Customer Service PII Auto-Sanitize
  description: Automatically masks Chinese ID cards, phone numbers, and email addresses
  enabled: true
  action: sanitize
  when:
    has_sensitive: true
    pattern_types:
      - id_card_cn
      - phone_cn
      - email_address
  source: user
```

**Example 2: Financial Application**
```bash
./openclaw-skill-generate-rule.py \
  "Block all requests containing credit cards, Ethereum private keys, or mnemonic phrases" \
  --apply
```

**Example 3: Development Environment**
```bash
./openclaw-skill-generate-rule.py \
  "In development, block file deletion and system modification commands" \
  --apply
```

### Troubleshooting

**Error: Cannot connect to ClawVault**
- Ensure ClawVault is running: `curl http://localhost:8766/api/health`
- Check the URL with `--url` flag

**Error: Rule generation failed**
- Verify `OPENAI_API_KEY` is set in ClawVault environment
- Check ClawVault logs for errors

**Rules not taking effect**
- Restart ClawVault after applying rules
- Verify rules are enabled in `~/.ClawVault/rules.yaml`

### Advanced Usage

**Batch generation:**
```bash
# Generate rules from file
cat policies.txt | while read policy; do
  ./openclaw-skill-generate-rule.py "$policy" --json >> rules.json
done
```

**Custom model:**
```bash
./openclaw-skill-generate-rule.py \
  "Block high-risk content" \
  --model gpt-4 \
  --temperature 0.2
```

**Validation only:**
```bash
# Generate without applying
./openclaw-skill-generate-rule.py "Your policy" > rule.yaml

# Review and manually apply
cat rule.yaml
```

## More Examples

Additional examples will be added here as the project grows.

## Contributing

To contribute an example:

1. Create a new file in this directory
2. Add documentation in this README
3. Ensure the example is well-commented
4. Test thoroughly before submitting

## Support

For issues or questions:
- GitHub Issues: https://github.com/tophant-ai/ClawVault/issues
- Documentation: https://github.com/tophant-ai/ClawVault/tree/main/doc
