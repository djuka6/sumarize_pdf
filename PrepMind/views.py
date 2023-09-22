from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import ContentSerializer, CheckAnswerSerializer
from .mess_gen import process_message, process_message2
from drf_yasg.utils import swagger_auto_schema
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import os
from .models import SavedResponse
from .serializers import SavedResponseSerializer
from django.core.exceptions import ObjectDoesNotExist  
from transformers import GPT2Tokenizer
def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in bounding_box])


@swagger_auto_schema(method="post", request_body=ContentSerializer)
@api_view(["POST"])
def content_view(request):
    if request.method == "POST":
        serializer = ContentSerializer(data=request.data)
        if serializer.is_valid():
            i = 0
            received_text = serializer.validated_data["img_url"]
            formUrl = received_text
            print("OVO JE POCETAK: " + formUrl + " --- KRAJ ---")

            # Azure Form Recognizer logic
            endpoint = os.environ["AZURE_CS_ENDPOINT"]
            key = os.environ["AZURE_CS_KEY"]
            document_analysis_client = DocumentAnalysisClient(
                endpoint=endpoint, credential=AzureKeyCredential(key)
            )

            poller = document_analysis_client.begin_analyze_document_from_url(
                "prebuilt-read", formUrl
            )
            result = poller.result()

            text_to_send = []
            analyzed_content = []
            for page in result.pages:
                for line in page.lines:
                    analyzed_content.append(line.content)

            # Merge every 10 sentences
            for i in range(0, len(analyzed_content), 70):
                chunk = " ".join(analyzed_content[i : i + 70])
                text_to_send.append(chunk)

            def array_to_string(array, separator=' '):
                return separator.join(map(str, array))
            
            result = array_to_string(analyzed_content)
            def split_text_into_chunks(text, max_tokens=3200):
                print(f"Type of text: {type(text)}")
                print(f"Content of text (first 100 characters): {text[:100]}...")
                tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
                tokens = tokenizer.tokenize(text)
                
                chunks = []
                current_chunk = []
                current_token_count = 0
                
                for token in tokens:
                    current_token_count += 1
                    current_chunk.append(token)
                    
                    if current_token_count >= max_tokens:
                        chunks.append(tokenizer.convert_tokens_to_string(current_chunk))
                        current_chunk = []
                        current_token_count = 0
                        
                if current_chunk:  # Add any remaining tokens
                    chunks.append(tokenizer.convert_tokens_to_string(current_chunk))
                    
                return chunks

            def array_to_string(array, separator=' '):
                return separator.join(map(str, array))

           # Assuming analyzed_content is defined
            long_text = array_to_string(analyzed_content)
            chunks = split_text_into_chunks(long_text)
   
            i = 1  # Initialize the counter
            concatenated_responses = ""  # Initialize the concatenated responses string

            # Iterate through each chunk and process it
            for chunk in chunks:
                print("NOVI : " + chunk)
                processed_message = process_message(chunk, "text")
                
                # Save to the database
                saved_response = SavedResponse(
                    question=processed_message, answer=chunk
                )
                saved_response.save()
                
                sum_message = f"{i}. BAJAMALI chunk: {processed_message}"
                #print("Processed message " + sum_message)
                
                # Concatenate the processed messages
                concatenated_responses += processed_message + " "
                
                i += 1  # Increment the counter

            # Print the concatenated responses with the sentence "VUKOVII"
            print("VUKOVII " + concatenated_responses)
            
            processed_message_final = process_message(concatenated_responses, "quiz")

            
            return Response(
                {"data": processed_message_final},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="get")
@api_view(["GET"])
def get_all_responses(request):
    if request.method == "GET":
        all_responses = SavedResponse.objects.all()
        serializer = SavedResponseSerializer(all_responses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method="post", request_body=CheckAnswerSerializer)
@api_view(["POST"])
def check_view(request):
    if request.method == "POST":
        received_data = request.data
        question_id = received_data.get("id", None)
        answer = received_data.get("answer", "")

        if question_id is None:
            return Response(
                {"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Retrieve the question from the database
            saved_response = SavedResponse.objects.get(pk=question_id)
            print("OVO JE OBJEKAT: " + str(saved_response.answer))
        except ObjectDoesNotExist:
            return Response(
                {"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND
            )

        ans = process_message(saved_response.answer, answer, saved_response.question)

        # Your logic to check the answer based on saved_response.data goes here
        is_correct = True  # Placeholder, implement your own logic

        response_data = {"id": question_id, "rate": ans}
        return Response(response_data, status=status.HTTP_200_OK)
