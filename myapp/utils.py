import cv2
import numpy as np

def preprocesare_imagine(image_path):
    """Încarcă imaginea și aplică filtre pentru a evidenția bulele."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"A fost întâmpinată o eroare: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2
    )
    return img, gray, thresh

def gaseste_bule(thresh, width, height):
    """Găsește contururile care seamănă cu bule de test."""
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    question_cnts = []
    
    min_area = (width * height) * 0.0001  
    max_area = (width * height) * 0.01    

    for c in contours:
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h) 
        area = cv2.contourArea(c)

        if 0.8 <= ar <= 1.2 and min_area < area < max_area:
            question_cnts.append(c)
            
    return question_cnts

def extrage_raspunsuri(image_path, total_questions=10):
    """Funcția principală apelată din Django."""
    try:
        img, gray, thresh = preprocesare_imagine(image_path)
        h, w = img.shape[:2]
        
        contours = gaseste_bule(thresh, w, h)
        
        if len(contours) < total_questions * 4: 
            return {"error": "Nu s-au detectat destule bule. Încearcă o poză mai clară."}

        
        contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])
        
        question_rows = []
        row_buffer = []
        prev_y = cv2.boundingRect(contours[0])[1]

        for c in contours:
            y = cv2.boundingRect(c)[1]
            if abs(y - prev_y) > 20:
                row_buffer = sorted(row_buffer, key=lambda c: cv2.boundingRect(c)[0])
                if len(row_buffer) >= 4: 
                    question_rows.append(row_buffer[:4])
                row_buffer = []
            
            row_buffer.append(c)
            prev_y = y
        
        if row_buffer:
            row_buffer = sorted(row_buffer, key=lambda c: cv2.boundingRect(c)[0])
            if len(row_buffer) >= 4:
                question_rows.append(row_buffer[:4])

        detected_answers = {}
        options = ['A', 'B', 'C', 'D']

        limit = min(total_questions, len(question_rows))
        
        for q_idx in range(limit):
            row = question_rows[q_idx]
            bubbled = None
            max_pixels = 0 

            for i, c in enumerate(row):
                mask = np.zeros(thresh.shape, dtype="uint8")
                cv2.drawContours(mask, [c], -1, 255, -1)
                
                
                mask = cv2.bitwise_and(thresh, thresh, mask=mask)
                total = cv2.countNonZero(mask)

                if total > max_pixels:
                    max_pixels = total
                    bubbled = i
            
            if bubbled is not None:
                detected_answers[str(q_idx + 1)] = options[bubbled]

        return detected_answers

    except Exception as e:
        return {"error": str(e)}

def calculeaza_nota(student_answers, correct_answers):
    """Compară răspunsurile și calculează nota."""
    score = 0
    total = len(correct_answers)
    details = []

    for q_num, correct_ans in correct_answers.items():
        q_str = str(q_num)
        student_ans = student_answers.get(q_str, None)
        
        is_correct = (student_ans == correct_ans)
        if is_correct:
            score += 1
            
        details.append({
            "question": q_num,
            "student_ans": student_ans,
            "correct_ans": correct_ans,
            "is_correct": is_correct
        })

    final_grade = (score / total) * 10 if total > 0 else 1
    
    return {
        "nota": round(final_grade, 2),
        "total_corecte": score,
        "detalii": details
    }

