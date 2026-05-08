"""
Message handlers for the bot.
Handles text messages, voice messages, images, and documents.
"""

import time
from aiogram import Router, F
from aiogram.types import Message
from structlog import get_logger

from app.llm import get_llm_provider
from app.rag import get_rag_pipeline

logger = get_logger(__name__)

router = Router()


@router.message(F.text)
async def handle_text_message(message: Message) -> None:
    """Handle text messages - main Q&A functionality."""
    start_time = time.time()
    query = message.text.strip()
    
    if not query:
        return
    
    # Skip commands
    if query.startswith('/'):
        return
    
    # Send processing status
    processing_msg = await message.answer("🔍 Ищу информацию в регламентах...")
    
    try:
        # Get RAG pipeline and retrieve context
        rag_pipeline = get_rag_pipeline()
        
        # Retrieve relevant chunks (will be empty until vector search is implemented)
        chunks = await rag_pipeline.retrieve_with_reranking(query)
        
        # Format context
        context = rag_pipeline.format_context(chunks)
        sources = rag_pipeline.format_sources(chunks)
        
        # Get LLM provider and generate response
        llm_provider = get_llm_provider()
        
        if context:
            response = await llm_provider.generate_response(query, context=context)
        else:
            # No context found - respond honestly
            response = "В загруженных регламентах нет информации по этому вопросу.\n\nПожалуйста, перефразируйте вопрос или обратитесь к администратору."
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Delete processing message
        await processing_msg.delete()
        
        # Format response with sources if available
        if sources['count'] > 0:
            response += "\n\n<b>Источники:</b>\n"
            for i, src in enumerate(sources['sources'], 1):
                response += f"{i}. {src['document_title']}\n"
        
        await message.answer(response)
        
    except Exception as e:
        logger.error("Error processing message", error=str(e))
        await processing_msg.delete()
        await message.answer(
            "❌ Произошла ошибка при обработке запроса.\n"
            "Пожалуйста, попробуйте позже."
        )


@router.message(F.voice)
async def handle_voice_message(message: Message) -> None:
    """Handle voice messages - speech to text."""
    # Send processing status
    await message.answer("🎤 Распознаю голосовое сообщение...")
    
    try:
        # Download voice file
        file = await message.bot.get_file(message.voice.file_id)
        file_bytes = await message.bot.download_file(file.file_path)
        
        # Use Whisper for speech-to-text
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(file_bytes.read(), language="ru")
        transcribed_text = result["text"].strip()
        
        logger.info("Voice transcribed", text=transcribed_text[:50])
        
        # Process as text message
        if transcribed_text:
            await handle_text_message.__wrapped__(message)
        else:
            await message.answer("❌ Не удалось распознать речь. Попробуйте еще раз.")
            
    except Exception as e:
        logger.error("Error processing voice", error=str(e))
        await message.answer(
            "❌ Произошла ошибка при распознавании голоса.\n"
            "Пожалуйста, отправьте текст вместо голосового сообщения."
        )


@router.message(F.photo)
async def handle_photo(message: Message) -> None:
    """Handle photo messages - OCR."""
    await message.answer("📷 Распознаю текст на изображении...")
    
    try:
        # Get highest quality photo
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file.file_path)
        
        # Use pytesseract for OCR
        from PIL import Image
        import pytesseract
        import io
        
        image = Image.open(io.BytesIO(file_bytes.read()))
        text = pytesseract.image_to_string(image, lang='rus+eng')
        text = text.strip()
        
        logger.info("OCR completed", text=text[:50])
        
        if text:
            # Process extracted text as query
            await message.answer(f"📝 Распознанный текст:\n\n{text[:500]}")
            # Optionally process as question
            # await handle_text_message.__wrapped__(message)
        else:
            await message.answer("❌ Не удалось распознать текст на изображении.")
            
    except Exception as e:
        logger.error("Error processing photo", error=str(e))
        await message.answer(
            "❌ Произошла ошибка при распознавании изображения.\n"
            "Пожалуйста, отправьте текст вместо фото."
        )


@router.message(F.document)
async def handle_document(message: Message) -> None:
    """Handle document attachments."""
    await message.answer(
        "📎 Получен документ.\n\n"
        "Для индексации документа обратитесь к администратору.\n"
        "Я могу отвечать только на вопросы по уже загруженным регламентам."
    )
