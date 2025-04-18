import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables from .env file (if it exists)
load_dotenv()

# Twilio configuration
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

def send_twilio_message(to_phone_number: str, message: str) -> dict:
    """
    Send an SMS message using Twilio.
    
    Args:
        to_phone_number (str): The recipient's phone number in E.164 format (e.g., +1234567890)
        message (str): The message content to send
        
    Returns:
        dict: Result with success status and message
    """
    # Check if Twilio credentials are available
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        return {
            "success": False,
            "message": "Twilio credentials not found. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER environment variables."
        }
    
    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Send the SMS message
        twilio_message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
        
        return {
            "success": True,
            "message": f"Message sent successfully with SID: {twilio_message.sid}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error sending message: {str(e)}"
        }

def send_notification_to_student(student_id: int, message: str, db=None) -> dict:
    """
    Send a notification to a student.
    
    Args:
        student_id (int): The student's ID
        message (str): The message to send
        db: Database session (optional)
        
    Returns:
        dict: Result with success status and message
    """
    try:
        # Import here to avoid circular imports
        from database import get_db, Student
        
        # Get database session if not provided
        if db is None:
            db = next(get_db())
        
        # Get student from database
        student = db.query(Student).filter(Student.id == student_id).first()
        
        if not student:
            return {
                "success": False,
                "message": f"Student with ID {student_id} not found"
            }
        
        # Format phone number for Twilio (add + if needed)
        phone = student.phone
        if not phone.startswith('+'):
            phone = f"+{phone}"
        
        # Send message
        result = send_twilio_message(phone, message)
        
        # Add additional information
        if result["success"]:
            result["message"] = f"Notification sent to {student.name}: {result['message']}"
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error in send_notification_to_student: {str(e)}"
        }

def send_class_notification(class_schedule_id: int, message: str, db=None) -> dict:
    """
    Send a notification to all students enrolled in a class.
    
    Args:
        class_schedule_id (int): The class schedule ID
        message (str): The message to send
        db: Database session (optional)
        
    Returns:
        dict: Result with success status and message
    """
    try:
        # Import here to avoid circular imports
        from database import get_db, ClassEnrollment, Student
        
        # Get database session if not provided
        if db is None:
            db = next(get_db())
        
        # Get all students enrolled in the class
        enrollments = db.query(ClassEnrollment).filter(
            ClassEnrollment.class_schedule_id == class_schedule_id
        ).all()
        
        if not enrollments:
            return {
                "success": False,
                "message": f"No students found enrolled in class with ID {class_schedule_id}"
            }
        
        # Collect results
        results = {
            "success": True,
            "total": len(enrollments),
            "sent": 0,
            "failed": 0,
            "details": []
        }
        
        # Send notification to each student
        for enrollment in enrollments:
            student = db.query(Student).filter(Student.id == enrollment.student_id).first()
            
            if student:
                # Format phone number for Twilio (add + if needed)
                phone = student.phone
                if not phone.startswith('+'):
                    phone = f"+{phone}"
                
                # Send message
                result = send_twilio_message(phone, message)
                
                # Add to results
                if result["success"]:
                    results["sent"] += 1
                else:
                    results["failed"] += 1
                
                results["details"].append({
                    "student_id": student.id,
                    "student_name": student.name,
                    "success": result["success"],
                    "message": result["message"]
                })
        
        # Update success status based on results
        if results["failed"] == results["total"]:
            results["success"] = False
            results["message"] = "Failed to send all notifications"
        elif results["failed"] > 0:
            results["message"] = f"Sent {results['sent']} notifications, {results['failed']} failed"
        else:
            results["message"] = f"Successfully sent notifications to all {results['total']} students"
        
        return results
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error in send_class_notification: {str(e)}"
        }


# Example usage
if __name__ == "__main__":
    # This code will run if you execute this file directly
    
    # Example: Send a direct message
    test_number = "+1234567890"  # Replace with a real number for testing
    result = send_twilio_message(test_number, "Test message from College Management System")
    print(result)