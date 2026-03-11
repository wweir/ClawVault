# ClawVault Changelog

## 2026-03-11 - Generative Rule Engine

### New Features

#### 🎯 LLM-Based Rule Generation
- **Module**: `src/claw_vault/guard/rule_generator.py`
  - Implemented `RuleGenerator` class for converting natural language to YAML rules
  - Comprehensive system prompt with 55+ pattern types and examples
  - Support for single and multiple rule generation
  - Built-in rule validation and explanation capabilities
  - Automatic rule structure verification and security warnings

#### 🔌 API Endpoints
- **Path**: `src/claw_vault/dashboard/api.py`
  - `POST /api/rules/generate` - Generate rules from natural language
  - `POST /api/rules/validate` - Validate rule structure and security
  - `POST /api/rules/explain` - Get human-readable rule explanations
  - Request/Response models: `GenerateRuleRequest`, `GenerateRuleResponse`, `ValidateRuleRequest`, `ValidateRuleResponse`

#### 📚 Documentation
- **File**: `doc/GENERATIVE_RULES.md` (comprehensive guide)
  - Complete API reference with examples
  - 5 practical use cases (customer service, finance, dev environment, API key management, prompt injection)
  - Rule structure specification
  - Python SDK usage examples
  - Best practices and troubleshooting

- **File**: `doc/OPENCLAW_INTEGRATION.md` (updated)
  - Added "Generative Rules for OpenClaw" section
  - 3 common OpenClaw use cases with generated rules
  - OpenClaw Skill integration example
  - API reference for integration
  - Environment-specific configurations
  - Troubleshooting guide

#### 🛠️ OpenClaw Skill
- **File**: `examples/openclaw-skill-generate-rule.py`
  - Standalone Python script for OpenClaw integration
  - Command-line interface for rule generation
  - Automatic rule application with `--apply` flag
  - JSON output support for programmatic use
  - Built-in examples and help text

### Use Cases Implemented

1. **Customer Service PII Protection**
   - Auto-sanitize Chinese ID cards, phone numbers, emails
   - Policy: "对于客服场景,如果检测到中国身份证号、手机号或邮箱地址,自动脱敏处理"

2. **Financial Security**
   - Block credit cards, crypto private keys, mnemonic phrases
   - Policy: "阻止所有包含信用卡号、以太坊私钥或助记词的请求"

3. **Development Environment Protection**
   - Block dangerous commands (file deletion, system modification, network requests)
   - Policy: "在开发环境中,阻止包含文件删除、系统修改或网络请求的危险命令"

4. **Tiered API Key Management**
   - High-risk (≥7.0): Block
   - Medium-risk (<7.0): Sanitize
   - Policy: "对于风险评分低于7.0的API密钥自动脱敏,风险评分7.0及以上的直接阻止"

5. **Prompt Injection Defense**
   - Block all injection and jailbreak attempts
   - Policy: "阻止所有Prompt注入和越狱尝试"

### Technical Details

**LLM Integration:**
- Uses OpenAI API (gpt-4o-mini by default)
- Temperature: 0.1 for deterministic output
- Lazy initialization of LLM client
- Graceful error handling and logging

**Rule Validation:**
- Action type verification (allow/block/sanitize/ask_user)
- ID format checking (kebab-case)
- Condition completeness validation
- Security risk warnings (e.g., allowing injections)

**API Features:**
- YAML string response format for rules endpoint
- Multiple rule generation support
- Comprehensive error messages
- Structured logging with structlog

### Files Modified

1. `src/claw_vault/guard/rule_generator.py` - NEW (389 lines)
2. `src/claw_vault/dashboard/api.py` - MODIFIED (added 153 lines)
3. `doc/GENERATIVE_RULES.md` - NEW (580 lines)
4. `doc/OPENCLAW_INTEGRATION.md` - MODIFIED (added 281 lines)
5. `examples/openclaw-skill-generate-rule.py` - NEW (280 lines)

### Dependencies

**Required:**
- `openai` - For LLM-based rule generation
- `pyyaml` - For YAML parsing and generation
- `requests` - For API client (OpenClaw Skill)

**Installation:**
```bash
pip install openai pyyaml requests
```

### Configuration

**Environment Variables:**
```bash
export OPENAI_API_KEY="sk-your-api-key"
```

### Testing

**Test rule generation:**
```bash
curl -X POST http://localhost:8766/api/rules/generate \
  -H 'Content-Type: application/json' \
  -d '{"policy": "Block all AWS credentials"}'
```

**Test with OpenClaw Skill:**
```bash
python examples/openclaw-skill-generate-rule.py "Block all prompt injections"
```

### Migration Notes

- No breaking changes
- Existing rules continue to work
- New API endpoints are additive
- LLM client is optional (only needed for generation)

### Known Limitations

1. Requires OpenAI API key for rule generation
2. LLM responses may vary slightly between calls
3. Complex policies may require manual refinement
4. Rule validation is heuristic-based

### Future Enhancements

- Support for additional LLM providers (Anthropic, local models)
- Dashboard UI for rule generation
- Rule templates library
- Batch rule generation
- Rule testing framework
- Rule versioning and rollback

---

## 2026-03-11 - Dashboard Optimization

### Features

- Fixed Configuration page issues (Run Test navigation, Hide/Show Details toggle, Custom Rules YAML display)
- Added 30+ new detection patterns from security projects
- Implemented Cards/Table view toggle for Quick Test page
- Created Attack Cases page with 15 real-world examples

### Files Modified

1. `src/claw_vault/dashboard/static/index.html` - MODIFIED
2. `src/claw_vault/dashboard/api.py` - MODIFIED
3. `src/claw_vault/detector/patterns.py` - MODIFIED

---

## 2026-03-10 - Custom Rule Engine

### Features

- Added custom rule engine support with YAML-backed rules
- Dashboard editor for managing rules
- API endpoints for rule CRUD operations

### Files Modified

1. `src/claw_vault/guard/rules_store.py` - NEW
2. `src/claw_vault/guard/rule_engine.py` - MODIFIED
3. `src/claw_vault/dashboard/api.py` - MODIFIED
4. `src/claw_vault/dashboard/static/index.html` - MODIFIED
