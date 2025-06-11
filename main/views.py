from django.shortcuts import render
from main.serializers import *
from rest_framework import status
from rest_framework.views import *
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import *
from .serializers import *
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta, timezone
#Views de Autenticação do usuário:
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'message':f'Bem Vindo, {request.user.username}! Esta é um rota protegida.'})
class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({"detail": "Refresh token not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({'access_token': access_token})
        except Exception:
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED)
class RegisterView(APIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                'access_token': str(refresh.access_token), 
                'refresh_token': str(refresh), 
                'user': serializer.data  
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
        response.delete_cookie('refresh_token')
        return response

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"detail": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response = Response({
                'access_token': access_token
            })

            response.set_cookie(
                key='refresh_token',
                value=str(refresh_token),
                httponly=True,
                secure=False,  # True em produção com HTTPS
                samesite='Lax',
                path='/',
                max_age=7 * 24 * 60 * 60,  # <- cookie válido por 7 dias
            )

            return response
        else:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)




#Views da Sessão:
class CreateSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            name = request.data.get('name')
            if not name:
                return Response({'message': 'Nome é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

            Session.objects.create(name=name, user=request.user)
            return Response({'message': 'Sessão criada com sucesso.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': f'Erro: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        
class ListSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try: 
            sessions = Session.objects.filter(user=request.user).all()
            print(sessions)
            serializer = SessionSerializer(sessions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':f'Erro: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        
class EditSessionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, id):
        try:
            name = request.data.get('name')
            if not name or not id:
                return Response({'message':'Parâmetros incorretos.'}, status=status.HTTP_400_BAD_REQUEST)
            session = Session.objects.filter(id=id).first()
            session.name = name
            session.save()
            return Response({'message':'Edição realizada.'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'message':e},status=status.HTTP_400_BAD_REQUEST)
    
class RemoveSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        try:
            if not id:
                return Response({'message':'ID is required.'}, status=400)
            session = Session.objects.filter(id=id).first()
            session.delete()
            return Response({'message':'Sucesso ao deletar sessão'}, status=200)
        except Exception as e:
            return Response({'message':e}, status=400)
        
#views sessão individual
class SingleSessionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            id_session = request.query_params.get('id_session')
            if not id_session:
                return Response({'message': 'id_session não fornecido.'}, status=status.HTTP_400_BAD_REQUEST)

            session = Session.objects.filter(id=id_session).first()
            if not session:
                return Response({'message': 'Sessão não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
            
            exercises = Exercise.objects.filter(session_id=id_session).all()
            exer_serializer = ExerciseSerializer(exercises, many=True)
            
            session_serializer = SessionSerializer(session)
            context = {
                "exercises" : exer_serializer.data,
                "session" : session_serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'message':f'Erro: {e}'}, status=status.HTTP_400_BAD_REQUEST)

class EndSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        try:
            duration = request.data.get('duration')
            exercises = request.data.get('exercises')

            session = Session.objects.filter(id=id).first()

            if not session:
                return Response({'message': 'Erro ao encontrar sessão'}, status=status.HTTP_404_NOT_FOUND)

            done_session = DoneSession.objects.create(
                session=session,
                duration=duration,
                date_finished=datetime.now()
            )

            exercises = Exercise.objects.filter(session=session.id).all()

            for e in exercises:
                DoneExercise.objects.create(
                    done_session=done_session,
                    position=e.position,
                    reps=e.reps,
                    makes=e.makes,
                    accuracy=e.accuracy,
                )


                e.makes = 0
                e.accuracy = 0.00
                e.checked = False
                e.save()
            
            session.save()
            return Response({'message':'Sessão finalizada com sucesso'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':'Erro ao finalizar sessão: {}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)

class CreateExerciseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try: 
            name = request.data.get('name')
            position = request.data.get('position', 'midrange-r')
            reps = int(request.data.get('reps'))
            session_id = request.data.get('session_id')
            session = Session.objects.filter(id=session_id).first()
            exercise = Exercise.objects.create(name=name, position=position, reps=reps, makes=0, accuracy=0, checked=0, session=session)
            serializers = ExerciseSerializer(exercise)
            return Response({'message':'Exercício criado com sucesso', "data": serializers.data}, status=status.HTTP_201_CREATED  )
        except Exception as e:
            return Response({'message':f'Erro: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        
        
    
class EditExerciseView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id): #finaliza o exer
        try:
            makes = int(request.data.get('makes'))
            
            if not id or makes is None:
                return Response({'message': 'ID e makes são obrigatórios'}, status=400)
            
            exer = Exercise.objects.filter(id=id).first()
            accuracy = (int(makes) / exer.reps) * 100 if exer.reps > 0 else 0
            exer.makes = makes
            exer.accuracy = accuracy
            exer.checked = 1
            exer.save()

            serializers = ExerciseSerializer(exer)
            return Response({'message':'Exercício concluído', 'exer': serializers.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':f'Erro: {e}'}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, id):
        try:
            name = request.data.get('name')
            position = request.data.get('position')
            reps = request.data.get('reps', 0)

            if not id or name == '':
                return Response({'message':'Parametros Invalidos.'}, status=status.HTTP_400_BAD_REQUEST)
            
            exer = Exercise.objects.filter(id=id).first()
            exer.name = name
            exer.position = position
            exer.reps = reps
            exer.makes = 0
            exer.accuracy = 0
            exer.save()
            return Response({'message':'Sucesso.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message':e}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, id):
        try: 
            exer = Exercise.objects.filter(id=id).first()
            if exer:
                exer.delete()
            return Response({'message':'Exercício removido'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message":f"Erro: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        




#tasks views

class CreateTask(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            name = request.data.get('name')
            checked = 0
            if name == "":
                return Response({'message':'O nome é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
            Tasks.objects.create(
                user=user,
                name = name,
                checked = checked
            )
            return Response({"message":"Criado com sucesso."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':e}, status=status.HTTP_400_BAD_REQUEST)

class EditTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        checked = request.data.get('checked', 0)
        try:
            task = Tasks.objects.filter(id=id).first()
            if not task:
                return Response({'message': 'Tarefa não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

            task.checked = checked
            task.save()
            return Response({'message': 'Salvo com sucesso'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'Erro: {e}'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            id = request.data.get('id')
            if not id:
                return Response({'message': 'ID não encontrado.'}, status=status.HTTP_401_UNAUTHORIZED)
            task = Tasks.objects.filter(id=id).first()
            task.delete()
            return Response({'message':'Removido com sucesso.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': e}, status=status.HTTP_400_BAD_REQUEST)
            

    
    def put(self, request, id):

        if not id:
                return Response({'message':'o ID é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        task = Tasks.objects.filter(id=id).first()
        novo_nome = request.data.get('novo_nome')

        if novo_nome != '':
            task.name = novo_nome
            task.checked = 0
            task.save()
        else:
            return Response({'message':'O nome não pode ser vazio'}, status=status.HTTP_400_BAD_REQUEST)

class ListTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            tasks = Tasks.objects.filter(user=request.user).all()
            serializer = TasksSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':e}, status=status.HTTP_200_OK)


class ClearCheckedTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            Tasks.objects.filter(checked=True).delete()
            return Response({'message': 'Removidas com sucesso'}, status=200)
        except Exception as e:
            return Response({'message': str(e)}, status=400)
        

#done sessions

class GetDoneSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            sessions = DoneSession.objects.all()
            data = []

            if not sessions.exists():
                return Response({'message': 'Nenhuma sessão encontrada'}, status=200)

            for done in sessions:
                session_data = {
                    'id': done.session.id if done.session else None,
                    'name': done.session.name if done.session else None,
                    'exercises': [],
                    'duration': done.duration,
                    'date_finished': done.date_finished
                }

                exercises = done.done_exercises.all()

                session_data['exercises'] = [
                    {
                        'id': exercise.id,
                        'name': exercise.name,
                        'position': exercise.position,
                        'reps': exercise.reps,
                        'makes': exercise.makes,
                        'accuracy': exercise.accuracy,
                    } for exercise in exercises
                ]
                
                data.append(session_data)

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'Error: {e}'}, status=400)

        
class ClearDoneSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            ids = request.data.get('ids', [])
        except Exception:
            return Response({'detail': 'Invalid request body.'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(ids, list):
            return Response({'detail': 'IDs must be provided as a list.'}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count = 0
        if ids:
            deleted_count, _ = DoneSession.objects.filter(session__id__in=ids).delete()
            


        return Response({'detail': f'{deleted_count} sessions deleted.'}, status=status.HTTP_200_OK)
        
