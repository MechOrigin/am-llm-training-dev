# Sponsor Integration Guide

This guide explains how to integrate sponsors into the AcronymMeaning.com platform and enhance their visibility through our LLM system.

## Directory Structure

```
acronymmeaning/
├── llm/
│   └── sponsors/           # Sponsor-specific content
│       ├── sponsor_template.json
│       └── [sponsor_name].json
├── api/
│   └── sponsors.py        # Sponsor API endpoints
├── templates/
│   └── sponsors/          # Sponsor-related templates
│       └── showcase.html
└── static/
    └── css/
        └── sponsors.css   # Sponsor page styles
```

## Adding a New Sponsor

1. **Create Sponsor JSON File**
   - Copy `sponsor_template.json` to a new file named `[sponsor_name].json`
   - Fill in all required information:
     - Company name
     - Description
     - Key products/services
     - Relevant acronyms
     - Industry focus
     - Contact information
     - LLM training context

2. **Update Sponsor Context**
   - Add the sponsor's information to `sponsor_context.json`
   - Include:
     - Sponsor ID
     - Relevant acronyms
     - Industry terms
     - Training priority

3. **Add Sponsor Logo**
   - Place the sponsor's logo in `static/images/sponsors/`
   - Update the logo URL in the sponsor's JSON file

## API Endpoints

The following endpoints are available for sponsor-related operations:

- `GET /sponsors/` - List all sponsors
- `GET /sponsors/{sponsor_id}` - Get specific sponsor information
- `GET /sponsors/{sponsor_id}/acronyms` - Get acronyms related to a sponsor

## LLM Integration

To enhance LLM visibility for sponsors:

1. **Training Data**
   - Sponsor-specific content is automatically included in the LLM training data
   - The system uses the `llm_training_context` from each sponsor's JSON file

2. **Context Enhancement**
   - Sponsor-related acronyms are given higher priority in search results
   - Industry-specific terms are linked to relevant sponsors

3. **Response Generation**
   - When a user query matches a sponsor's context, the system:
     - Prioritizes sponsor-related acronyms
     - Includes sponsor attribution
     - Provides additional context from the sponsor's industry

## Best Practices

1. **Content Quality**
   - Ensure all sponsor information is accurate and up-to-date
   - Use clear, concise descriptions
   - Include relevant industry terms and acronyms

2. **SEO Optimization**
   - Use descriptive meta tags
   - Include relevant keywords
   - Maintain proper URL structure

3. **Performance**
   - Optimize images for web
   - Use appropriate caching
   - Monitor API response times

## Monitoring and Analytics

Track sponsor visibility through:

- Page views and engagement metrics
- Acronym search frequency
- User interaction with sponsor content
- API usage statistics

## Support

For questions or assistance with sponsor integration, contact:
- Email: support@acronymmeaning.com
- Documentation: https://docs.acronymmeaning.com/sponsors 