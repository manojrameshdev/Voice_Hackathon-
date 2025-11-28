print("🤖 Testing DoseBuddy AI Assistant...")
print("=" * 60)

try:
    from ai_assistant import test_api_connection, get_ai_response
    
    # Test connection
    success, message = test_api_connection()
    print(message)
    print("=" * 60)
    
    if success:
        print("\n✅ Testing AI Response...")
        print("-" * 60)
        response = get_ai_response("What is Paracetamol used for?", "")
        print(f"AI Response:\n{response}")
        print("-" * 60)
        print("\n✅ Your AI Assistant is fully functional!")
        print("Run: streamlit run app.py")
    else:
        print("\n❌ Please configure your API key first")
        print("Visit: https://aistudio.google.com/app/apikey")
        
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\nMake sure you have:")
    print("1. Saved the updated ai_assistant.py")
    print("2. Installed: pip install google-generativeai")
    
except Exception as e:
    print(f"❌ Error: {e}")
