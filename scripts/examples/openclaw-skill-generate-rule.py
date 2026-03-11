#!/usr/bin/env python3
"""
ClawVault Rule Generator Skill for OpenClaw

This Skill allows you to generate security rules from natural language
directly within OpenClaw.

Usage:
    openclaw skill run generate-rule "Block all AWS credentials"
    openclaw skill run generate-rule "Auto-sanitize PII data in customer service"

Requirements:
    - ClawVault running on localhost:8766
    - OPENAI_API_KEY set in ClawVault environment
"""

import argparse
import json
import sys
from typing import Optional

try:
    import requests
    import yaml
except ImportError:
    print("Error: Required packages not installed")
    print("Install with: pip install requests pyyaml")
    sys.exit(1)


class ClawVaultRuleGenerator:
    """Client for ClawVault generative rule API."""
    
    def __init__(self, base_url: str = "http://localhost:8766"):
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
    
    def generate_rule(
        self, 
        policy: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
        multiple: bool = False
    ) -> Optional[dict]:
        """Generate security rule(s) from natural language policy.
        
        Args:
            policy: Natural language description of security policy
            model: LLM model to use
            temperature: LLM temperature (0.0-1.0)
            multiple: Generate multiple rules if needed
            
        Returns:
            API response dict or None on error
        """
        try:
            response = requests.post(
                f"{self.api_url}/rules/generate",
                json={
                    "policy": policy,
                    "model": model,
                    "temperature": temperature,
                    "multiple": multiple
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"✗ API request failed: HTTP {response.status_code}")
                print(f"  {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("✗ Cannot connect to ClawVault")
            print(f"  Ensure ClawVault is running at {self.base_url}")
            return None
        except Exception as exc:
            print(f"✗ Error: {exc}")
            return None
    
    def apply_rules(self, rules: list[dict]) -> bool:
        """Apply generated rules to ClawVault.
        
        Args:
            rules: List of rule dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current rules
            response = requests.get(f"{self.api_url}/config/rules")
            if response.status_code != 200:
                print("✗ Failed to get current rules")
                return False
            
            current_yaml = response.text
            current_rules = yaml.safe_load(current_yaml) if current_yaml else []
            
            # Merge new rules
            all_rules = current_rules + rules
            
            # Upload merged rules
            response = requests.post(
                f"{self.api_url}/config/rules",
                json={"rules": all_rules}
            )
            
            if response.status_code == 200:
                print(f"✓ Successfully applied {len(rules)} rule(s)")
                return True
            else:
                print(f"✗ Failed to apply rules: HTTP {response.status_code}")
                return False
                
        except Exception as exc:
            print(f"✗ Error applying rules: {exc}")
            return False


def print_rule_info(result: dict) -> None:
    """Pretty print rule generation result."""
    if not result.get("success"):
        print(f"✗ Rule generation failed: {result.get('error', 'Unknown error')}")
        return
    
    rules = result.get("rules", [])
    if not rules:
        print("✗ No rules generated")
        return
    
    print(f"✓ Generated {len(rules)} rule(s)\n")
    
    # Print explanation
    if result.get("explanation"):
        print("=" * 60)
        print("EXPLANATION")
        print("=" * 60)
        print(result["explanation"])
        print()
    
    # Print warnings
    if result.get("warnings"):
        print("⚠ WARNINGS:")
        for warning in result["warnings"]:
            print(f"  - {warning}")
        print()
    
    # Print YAML
    print("=" * 60)
    print("GENERATED YAML")
    print("=" * 60)
    print(yaml.dump(rules, sort_keys=False, allow_unicode=True))


def main():
    parser = argparse.ArgumentParser(
        description="Generate ClawVault security rules from natural language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Block all AWS credentials"
  %(prog)s "Auto-sanitize PII data" --apply
  %(prog)s "Block high-risk content above 8.0" --multiple
  %(prog)s "Protect API keys in development" --url http://remote-server:8766

Common Policies:
  - "Block all prompt injection attempts"
  - "Auto-sanitize sensitive data with risk score above 7.0"
  - "Block requests containing OpenAI API keys"
  - "Sanitize Chinese ID cards, phone numbers, and emails"
  - "Block dangerous shell commands"
        """
    )
    
    parser.add_argument(
        "policy",
        help="Natural language description of security policy"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8766",
        help="ClawVault base URL (default: http://localhost:8766)"
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="LLM model to use (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="LLM temperature 0.0-1.0 (default: 0.1)"
    )
    parser.add_argument(
        "--multiple",
        action="store_true",
        help="Generate multiple rules if needed"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Automatically apply generated rules to ClawVault"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of formatted text"
    )
    
    args = parser.parse_args()
    
    # Create client
    client = ClawVaultRuleGenerator(args.url)
    
    # Generate rule
    print(f"Generating rule for: {args.policy}\n")
    result = client.generate_rule(
        args.policy,
        model=args.model,
        temperature=args.temperature,
        multiple=args.multiple
    )
    
    if not result:
        sys.exit(1)
    
    # Output result
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_rule_info(result)
    
    # Apply if requested
    if args.apply and result.get("success"):
        print("\nApplying rules to ClawVault...")
        if client.apply_rules(result["rules"]):
            print("✓ Rules are now active!")
        else:
            print("✗ Failed to apply rules")
            sys.exit(1)
    elif result.get("success"):
        print("\nTo apply these rules, run with --apply flag")
        print(f"  {sys.argv[0]} \"{args.policy}\" --apply")


if __name__ == "__main__":
    main()
