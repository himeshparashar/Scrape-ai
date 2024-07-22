async def  voice_and_tone(req:BrandVoiceToneReq, max_token:int=100)->str:
    # Selecting URL to push generated voice and tone data
    if req.env == 'production':
        # Production URL
        url = "https://api.ayecampaigns.com/auth/update_brand_status"
    else:
        # QA URL
        url='https://qa-api.ayecampaigns.com/auth/update_brand_status'


    try:
        # Handling TEXT type data
        if req.file_type.lower() == 'text':
            context_data = req.content
            kn = await knowledgebase_text_processor(request=req)
        
        # Handling PDF type data
        elif req.file_type.lower() == 'pdf':
            kn = await knowledgebase_pdf_collecton(
                collection_name=req.collection_name,
                files=req.content,
                collection_id=req.collection_id,
                user_id=req.user_id,
            )
            context_data = ""
            loader = PyPDFLoader(req.content)
            pages = loader.load_and_split()
            for page in pages:
                context_data += page.page_content
            context_data = context_data[:1000]
        
        # Handling Web Scrapping
        elif req.file_type.lower() == 'url':
            # Scraping data from website
            webs = WebScrapper()
            web_data = webs._run_scrape_page(req.content)
            # If web content is not null add them into collection
            if req.is_cron:
                collection_name = req.collection_name
                kn = req.collection_name
            else:
                collection_name = req.collection_name+"_"+req.collection_id
                kn = req.collection_name+"_"+req.collection_id

            if web_data and web_data !='':
                web_data_loader = await text_loader(web_data)
                metadata = {
                    "collection_name": collection_name,
                    "collection_id": req.collection_id,
                    "user_id": req.user_id,
                }
                is_added = await LangChainVectorStore.run_db(
                    docs = web_data_loader, 
                    collection_name = collection_name,
                    metadata=metadata, 

                )
                kn = collection_name

                context_data = web_data[:1000]
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Unable to scrap url."
                )
        else:
            print('Unknown file type')
  
        

        print("Collection created successfully, working on voice generation")   

        # Voice generation prompt 
        prompt = f"""
        AI Assistant Role: Sr. brand manager
        Task: Generate a brand voice and tone based on the following text
        Style: Business
        Tone: Professional
        Length: {max_token} words
        Format: Text
        context_data:\n
        {context_data}
        """

        # Define LLM chain
        llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo", api_key=os.environ.get('OPENAI_API_KEY'))
        llm_tokens = llm.get_num_tokens(prompt)

        # Handling token overflow
        if llm_tokens > 4000:
            print('Too many tokens')
            res = requests.post(                
                url = url,
                json={
                    "collection_name" : kn,
                    "status" : "FAILED",
                    "voice" : "None"
                },
                headers={
                    "Content-Type": "application/json"
                }
            )
        
        # Run the LLM Agent
        brand_voice = llm.invoke(prompt).content

        # Push Brand voice data to server
        status, res = await make_request(
            url = url,
            kn = kn,
            status="ACTIVE",
            voice=brand_voice
        )
        # res = requests.post(                
        #     url = url,
        #     json={
        #         "collection_name" : kn,
        #         "status" : "ACTIVE",
        #         "voice" : brand_voice
        #     },
        #     headers={
        #         "Content-Type": "application/json"
        #     }
        # )

        # Check request status
        if status == 200:
            print("Voice generated successfully")
        else:
            print("Actual status code : ", status)
            status, res = await make_request(
                url = url,
                kn = kn,
                status="FAILED",
                voice=brand_voice
            )
            print(res, status)
            print("Got some error response while pushing voice data to server")

    except Exception as e:
        print(e)
        status, res = await make_request(
            url = url,
            kn = kn,
            status="FAILED",
            voice=None
        )
        print(res, status)
        error_message = str(e)
        print(error_message)
    
