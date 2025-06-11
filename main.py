import requests
import json

url = "https://your-agent.onrender.com/create-notion-page"

payload = {
  "parent": { "database_id": "20e32305c879807587a8e770476f65dc" },
  "properties": {
    "Title": { "title": [{ "text": { "content": "Harnessing Quiet Tech: Open-Source, Subtle AI, and Viral Reach" } }] },
    "Slug": { "rich_text": [{ "text": { "content": "harnessing-quiet-tech-open-source-subtle-ai-and-viral-reach" } }] },
    "Short Description": { "rich_text": [{ "text": { "content": "Explore how businesses can leverage open-source tools and understated AI startups." } }] },
    "Category": { "select": { "name": "Keyword Research" } },
    "Tags": { "multi_select": [] },
    "Publication Date": { "date": { "start": "2025-06-07T20:00:00Z" } },
    "Status": { "select": { "name": "Draft" } },
    "Full Description": {
      "rich_text": [
        {
          "type": "text",
          "text": {
            "content": "<h1>Harnessing Quiet Tech</h1><p>Full post content here...</p>"
          }
        }
      ]
    }
  },
  "cover": { "external": { "url": "https://yourcdn.com/path-to-image.jpg" } }
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, json=payload)
print("Response status:", response.status_code)
print("Response body:", response.text)
