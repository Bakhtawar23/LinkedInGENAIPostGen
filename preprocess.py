import json
from llm_helper import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException


def sanitize_text(text):
    """Sanitize text to handle Unicode surrogates and encoding issues"""
    if isinstance(text, str):
        # Handle Unicode surrogates by encoding and decoding with error handling
        return text.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
    return text


def extract_metadata(post):
    # Sanitize the post text before processing
    sanitized_post = sanitize_text(post)

    template = '''
    You are given a LinkedIn post. You need to extract number of lines, language of the post and tags.
    1. Return a valid JSON. No preamble. 
    2. JSON object should have exactly three keys: line_count, language and tags. 
    3. tags is an array of text tags. Extract maximum two tags.
    4. Language should be English or Hinglish (Hinglish means hindi + english)

    Here is the actual post on which you need to perform this task:  
    {linkedinpost}
    '''

    pt = PromptTemplate.from_template(template)
    chain = pt | llm

    try:
        response = chain.invoke(input={"linkedinpost": sanitized_post})
    except Exception as e:
        # Fallback: return default metadata if LLM call fails
        print(f"Error processing post with LLM: {e}")
        return {"line_count": 0, "language": "Unknown", "tags": []}

    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse metadata.")
    return res


def get_unified_tags(enriched_posts):
    unique_tags = set()
    # Loop through each post and extract the tags
    for post in enriched_posts:
        # Sanitize tags before adding to set
        sanitized_tags = [sanitize_text(tag) for tag in post.get('tags', [])]
        unique_tags.update(sanitized_tags)

    unique_tags_list = ','.join(unique_tags)

    template = '''I will give you a list of tags. You need to unify tags with the following requirements,
    1. Tags are unified and merged to create a shorter list. 
       Example 1: "Jobseekers", "Job Hunting" can be all merged into a single tag "Job Search". 
       Example 2: "Motivation", "Inspiration", "Drive" can be mapped to "Motivation"
       Example 3: "Personal Growth", "Personal Development", "Self Improvement" can be mapped to "Self Improvement"
       Example 4: "Scam Alert", "Job Scam" etc. can be mapped to "Scams"
    2. Each tag should be follow title case convention. example: "Motivation", "Job Search"
    3. Output should be a JSON object, No preamble
    4. Output should have mapping of original tag and the unified tag. 
       For example: {{"Jobseekers": "Job Search", "Job Hunting": "Job Search", "Motivation": "Motivation"}}

    Here is the list of tags: 
    {tags}
    '''

    # Sanitize the tags list before sending to LLM
    sanitized_tags = sanitize_text(unique_tags_list)

    pt = PromptTemplate.from_template(template)
    chain = pt | llm

    try:
        response = chain.invoke(input={"tags": sanitized_tags})
    except Exception as e:
        print(f"Error unifying tags with LLM: {e}")
        return {}

    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse tags.")
    return res


def process_post(raw_file_path, processed_file_path):
    enriched_posts = []

    try:
        with open(raw_file_path, 'r', encoding='utf-8') as file:
            posts = json.load(file)
    except Exception as e:
        print(f"Error reading raw posts file: {e}")
        return

    for post in posts:
        try:
            # Ensure post has the expected structure
            if 'text' not in post:
                print(f"Post missing 'text' field: {post}")
                continue

            metadata = extract_metadata(post['text'])
            post_with_metadata = {**post, **metadata}  # Compatible with all Python versions
            enriched_posts.append(post_with_metadata)
        except Exception as e:
            print(f"Error processing post: {e}")
            continue

    if not enriched_posts:
        print("No posts were successfully processed.")
        return

    try:
        unified_tags = get_unified_tags(enriched_posts)

        for post in enriched_posts:
            current_tags = post.get('tags', [])
            # Safely update tags with unified tags
            new_tags = set()
            for tag in current_tags:
                sanitized_tag = sanitize_text(tag)
                if sanitized_tag in unified_tags:
                    new_tags.add(unified_tags[sanitized_tag])
                else:
                    new_tags.add(sanitized_tag)  # Keep original if no mapping found
            post['tags'] = list(new_tags)

        # Write with ensure_ascii=False to preserve Unicode characters properly
        with open(processed_file_path, 'w', encoding='utf-8') as outfile:
            json.dump(enriched_posts, outfile, indent=4, ensure_ascii=False)

        print(f"Successfully processed {len(enriched_posts)} posts.")

    except Exception as e:
        print(f"Error in final processing: {e}")


if __name__ == "__main__":
    process_post("data/raw_posts.json", "data/processed_posts.json")