from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .firebase import initialize_firebase, verify_firebase_token
from firebase_admin import auth as admin_auth
from firebase_admin import firestore
from main.authenticate import EmailBackend as django_auth
import datetime
from .models import  User
import json

initialize_firebase()
db = firestore.client()

class SignupView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)  # Parse JSON request body
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            if not email or not password:
                return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

            # Create a user in Firebase
            user = admin_auth.create_user(display_name=name,email=email, password=password)
            User.objects.create_user(email=email, password=password)
            try :
                doc_ref = db.collection('clarity').document('user')
                doc_ref.set({
                    "uid":user.uid,
                    "username": name,
                    "year_of_study": "",
                    "department":"",
                    "branch":"",
                    "section":"",
                })
            except Exception as e:
                pass
            return Response({'message': 'User created successfully!', 'uid': user.uid}, status=status.HTTP_201_CREATED)

        except  admin_auth.EmailAlreadyExistsError:
            return Response({'error': 'Email already in use'}, status=status.HTTP_400_BAD_REQUEST)
        
        except ValueError as ve:  # Catch the ValueError properly
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(e)
            data = json.loads(request.body)  # Parse JSON request body
            email = data.get('email')
            password = data.get('password')
            if not email or not password:
                return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': e,"message":"SiginUp failed."}, status=status.HTTP_400_BAD_REQUEST)

class SigninView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body) 
            header = request.headers 
            token = header["Authorization"]
            email = data.get('email')
            password = data.get('password')
            if not email or not password:
                return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
            django_user = django_auth.authenticate(request, email=email, password=password)
            if django_user is not None:  
                user = verify_firebase_token(token)
                if not user:
                    return Response({"error": "Invalid credentials! check your email and password and try again."}, status=status.HTTP_400_BAD_REQUEST)   
                return Response({"message":"Sigged in successfully","user": user}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)  # Authentication failed
            
        except Exception as e:
            print(e)
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        try:
            token = request.headers["Authorization"]
            user = verify_firebase_token(token)
            if not user:
                 return Response({"error": "UID is required"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e :
            if e == "Invalid ID token":
                return Response({"error": "Logout failed","message":"you session has expired! SignIn again"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"error": "Logout failed","message":e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserProfileView(APIView):
    def post(self, request):
        token = request.headers["Authorization"]
        user = verify_firebase_token(token)
        if not user:
            print("from")
            return Response({"error": "UID is required"}, status=status.HTTP_400_BAD_REQUEST)
        doc_ref = db.collection('clarity').document('user')
        data = doc_ref.get()
        if not data:
            return Response({"error":"No data found!"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"data":user},status=status.HTTP_200_OK)