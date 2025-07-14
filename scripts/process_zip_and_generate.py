def generate_documents(context):
    for category, filenames in DOCUMENTS.items():
        for filename in filenames:
            title = filename.replace(".md", "")
            print(f"Generating {category}/{filename}...")

            output_path = OUTPUT_DIR / category / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Skip existing successful files
            if output_path.exists():
                with open(output_path, "r", encoding="utf-8") as f:
                    if "Error generating" not in f.read() and f.read().strip():
                        print(f"Skipping {filename} (already exists)")
                        continue

            system_prompt = BASE_SYSTEM_PROMPT.format(title=title)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is the source code and context:\n{context}"}
            ]

            prompt_length = sum(len(m["content"]) for m in messages)
            print(f"Prompt length for {title}: {prompt_length} characters")

            MAX_RETRIES = 3
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        temperature=0.3
                    )
                    content = response.choices[0].message.content
                    break
                except Exception as e:
                    if attempt == MAX_RETRIES:
                        content = f"Error generating {title}:\n\n{e}"
                    else:
                        print(f"Retrying {title} (attempt {attempt}) after error: {e}")
                        time.sleep(3 * attempt)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
