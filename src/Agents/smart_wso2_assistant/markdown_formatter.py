"""
Markdown Response Formatter for WSO2 Agent
Provides structured markdown formatting for analysis reports and critical findings.
"""

def format_comparison_report_as_markdown(report_data):
    """
    Formats a comparison report as structured markdown with enhanced visibility for critical sections.
    
    Args:
        report_data (dict): The comparison report containing findings and summary
        
    Returns:
        str: Formatted markdown string with structured sections
    """
    
    if not report_data or 'findings' not in report_data:
        return "## Analysis Complete\n\nNo findings to report."
    
    findings = report_data.get('findings', [])
    summary = report_data.get('summary', {})
    
    # Start with comparison overview
    markdown = "# 🔍 Code Comparison Analysis\n\n"
    
    if summary:
        total = summary.get('total', len(findings))
        genuine_gaps = summary.get('genuine_gaps', 0) 
        platform_diffs = summary.get('platform_diffs', 0)
        enhancements = summary.get('enhancements', 0)
        
        markdown += f"**Analysis Summary:** Found {total} items: {genuine_gaps} genuine gaps, {platform_diffs} platform differences, {enhancements} enhancement opportunities.\n\n"
    
    # Categorize findings
    critical_gaps = [f for f in findings if f.get('type') == 'GENUINE_GAP' and f.get('impact') == 'HIGH']
    important_gaps = [f for f in findings if f.get('type') == 'GENUINE_GAP' and f.get('impact') == 'MEDIUM']
    enhancements = [f for f in findings if f.get('type') == 'ENHANCEMENT_OPPORTUNITY']
    platform_diffs = [f for f in findings if f.get('type') == 'PLATFORM_DIFFERENCE']
    
    # Critical Gaps Section - Enhanced visibility
    if critical_gaps:
        markdown += "## 🚨 **CRITICAL GAPS**\n\n"
        markdown += "These are high-impact business logic differences that must be addressed:\n\n"
        
        for i, finding in enumerate(critical_gaps, 1):
            markdown += f"### {i}. {finding.get('details', 'Critical Finding')}\n\n"
            if finding.get('business_intent'):
                markdown += f"**Business Impact:** {finding['business_intent']}\n\n"
            if finding.get('wso2_fix'):
                markdown += f"**WSO2 Fix Required:** {finding['wso2_fix']}\n\n"
            markdown += "---\n\n"
    
    # Important Gaps Section
    if important_gaps:
        markdown += "## ⚠️ **IMPORTANT GAPS**\n\n"
        for i, finding in enumerate(important_gaps, 1):
            markdown += f"**{i}.** {finding.get('details', 'Important finding')}\n\n"
            if finding.get('wso2_fix'):
                markdown += f"*Fix:* {finding['wso2_fix']}\n\n"
    
    # Enhancement Opportunities Section
    if enhancements:
        markdown += "## 🔧 **ENHANCEMENT OPPORTUNITIES**\n\n"
        for i, finding in enumerate(enhancements, 1):
            markdown += f"**{i}.** {finding.get('details', 'Enhancement opportunity')}\n\n"
            if finding.get('wso2_fix'):
                markdown += f"*Suggestion:* {finding['wso2_fix']}\n\n"
    
    # Platform Differences Section
    if platform_diffs:
        markdown += "## ℹ️ **PLATFORM DIFFERENCES**\n\n"
        markdown += "These are expected differences due to platform variations:\n\n"
        for i, finding in enumerate(platform_diffs, 1):
            markdown += f"- {finding.get('details', 'Platform difference')}\n"
        markdown += "\n"
    
    # Overall Assessment
    if summary.get('overall_assessment'):
        markdown += "## 📊 **OVERALL ASSESSMENT**\n\n"
        markdown += f"{summary['overall_assessment']}\n\n"
    
    # Next Steps
    if critical_gaps or important_gaps:
        markdown += "## ✅ **NEXT STEPS**\n\n"
        markdown += "Would you like me to apply the recommended fixes to your WSO2 code?\n\n"
    else:
        markdown += "## ✅ **CONCLUSION**\n\n"
        markdown += "Your WSO2 implementation looks good! No critical issues found.\n\n"
    
    return markdown


def format_critical_section_only(critical_findings):
    """
    Formats only critical findings with enhanced visibility.
    
    Args:
        critical_findings (list): List of critical findings
        
    Returns:
        str: Formatted markdown for critical section only
    """
    
    if not critical_findings:
        return ""
    
    markdown = "## 🚨 **CRITICAL GAPS**\n\n"
    markdown += "**HIGH PRIORITY ISSUES REQUIRING IMMEDIATE ATTENTION:**\n\n"
    
    for i, finding in enumerate(critical_findings, 1):
        markdown += f"### Finding #{i}: Missing Property\n\n"
        markdown += f"**Details:** {finding.get('details', 'Critical business logic gap identified')}\n\n"
        
        if finding.get('business_intent'):
            markdown += f"**Business Impact:** {finding['business_intent']}\n\n"
            
        if finding.get('wso2_fix'):
            markdown += f"**Required Fix:** {finding['wso2_fix']}\n\n"
            
        markdown += "---\n\n"
    
    return markdown


def format_analysis_summary(analysis_type, key_findings):
    """
    Formats a simple analysis summary.
    
    Args:
        analysis_type (str): Type of analysis (e.g., "Apache Camel", "WSO2 Synapse")
        key_findings (list): List of key findings
        
    Returns:
        str: Formatted markdown summary
    """
    
    markdown = f"# ✅ {analysis_type} Analysis Complete\n\n"
    
    if key_findings:
        markdown += "## Key Findings:\n\n"
        for finding in key_findings:
            markdown += f"- {finding}\n"
        markdown += "\n"
    
    markdown += "Ready for the next step in the analysis process.\n\n"
    
    return markdown


def ensure_critical_section_visibility(content):
    """
    Ensures critical sections are properly formatted for UI visibility.
    
    Args:
        content (str): Original content
        
    Returns:
        str: Content with enhanced critical section formatting
    """
    
    # Add explicit formatting for critical sections
    if "CRITICAL" in content.upper() and "🚨" not in content:
        # If content mentions critical but lacks emoji, add structure
        content = content.replace("CRITICAL GAPS", "🚨 **CRITICAL GAPS**")
        content = content.replace("Critical Gaps", "🚨 **CRITICAL GAPS**")
        content = content.replace("CRITICAL SECTION", "🚨 **CRITICAL SECTION**")
    
    return content
