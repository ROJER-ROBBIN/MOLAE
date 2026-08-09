import os
import unittest
from parser import WhatsAppParser

class TestWhatsAppParser(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_chat.txt"
        self.parser = WhatsAppParser()
        
        # Write test data
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("8/6/24, 9:16 AM - Messages and calls are end-to-end encrypted.\n")
            f.write("1/2/25, 1:32 PM - ROBbiN ROjER: \n")
            f.write("1/2/25, 2:05 PM - ROBbiN ROjER: <Media omitted>\n")
            f.write("1/2/25, 7:56 PM - Chitraguptar!! : Rendume iruku\n")
            f.write("1/2/25, 8:04 PM - ROBbiN ROjER: Aahaa yosi da candle oil 😂 <This message was edited>\n")
            f.write("1/2/25, 8:05 PM - ROBbiN ROjER: 1. Random\n")
            f.write("2. Personal  \n")
            f.write("3. situational \n")
            f.write("   4.  Naughty \n")
            f.write("\n")
            f.write("Ethum illaya?😁\n")
            f.write("1/2/25, 8:06 PM - Chitraguptar!! : Kelu: time\n") # message with colon
            f.write("1/2/25, 8:06 PM - ROBbiN ROjER: தமிழ் and English!\n") # mixed language
            
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_parse_messages(self):
        messages = self.parser.parse_file(self.test_file)
        
        self.assertEqual(len(messages), 8)
        
        # Test 1: System message
        self.assertTrue(messages[0]['is_system'])
        self.assertEqual(messages[0]['sender'], None)
        
        # Test 2: Empty message
        self.assertEqual(messages[1]['sender'], 'ROBbiN ROjER')
        self.assertTrue(messages[1]['is_empty'])
        self.assertFalse(messages[1]['is_media'])
        
        # Test 3: Media omitted
        self.assertTrue(messages[2]['is_media'])
        self.assertEqual(messages[2]['text'], '<Media omitted>')
        
        # Test 4: Normal message
        self.assertEqual(messages[3]['text'], 'Rendume iruku')
        self.assertFalse(messages[3]['is_edited'])
        
        # Test 5: Edited message and emojis
        self.assertTrue(messages[4]['is_edited'])
        self.assertEqual(messages[4]['text'], 'Aahaa yosi da candle oil 😂')
        
        # Test 6: Multiline message
        self.assertTrue('\n' in messages[5]['text'])
        self.assertTrue('Ethum illaya?' in messages[5]['text'])
        
        # Test 7: Internal colon
        self.assertEqual(messages[6]['text'], 'Kelu: time')
        
        # Test 8: Mixed language
        self.assertEqual(messages[7]['text'], 'தமிழ் and English!')
        
if __name__ == '__main__':
    unittest.main()
