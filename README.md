This tool will analyze posts of a LinkedIn influencer and help them create the new posts based on the writing style in their old posts

<img width="1114" height="672" alt="image" src="https://github.com/user-attachments/assets/15ff08ce-f9da-4674-9186-c3fe0ca83601" />


Let's say Mohan is a LinkedIn influencer and he needs help in writing his future posts. He can feed his past LinkedIn posts to this tool and it will extract key topics. Then he can select the topic, length, language etc. and use Generate button to create a new post that will match his writing style.

Technical Architecture
<img width="1428" height="770" alt="image" src="https://github.com/user-attachments/assets/04fc8e44-c572-4834-8400-ac96adcf8f96" />


Stage 1: Collect LinkedIn posts and extract Topic, Language, Length etc. from it.

Stage 2: Now use topic, language and length to generate a new post. Some of the past posts related to that specific topic, language and length will be used for few shot learning to guide the LLM about the writing style etc.
