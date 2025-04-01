from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            tokens = response.data

            access_token = tokens['access']
            refresh_token = tokens['refresh']

            res = Response()

            res.data = {'success': True}

            res.set_cookie(
                key='access_token', 
                value=access_token, 
                httponly=True,
                secure=False,
                samesite='None',
                path='/'
            )

            res.set_cookie(
                key='refresh_token', 
                value=refresh_token, 
                httponly=True,
                secure=False,
                samesite='None',
                path='/'
            )

            return res

        except KeyError as e:
            return Response({'success': False, 'error': f'Missing token key: {str(e)}'}, status=400)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
        
class CustomRefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')

            request.data['refresh'] = refresh_token

            response = super().post(request, *args, **kwargs)

            tokens = response.data

            access_token = tokens['access']

            res = Response()

            res.data = {'refreshed': True}

            res.set_cookie(
                key='access_token', 
                value=access_token, 
                httponly=True,
                secure=True,
                samesite='None',
                path='/'
            )

            return res

        except KeyError as e:
            return Response({'refreshed': False, 'error': f'Missing token key: {str(e)}'}, status=400)
        except Exception as e:
            return Response({'refreshed': False, 'error': str(e)}, status=500)
