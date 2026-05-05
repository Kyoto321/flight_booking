from rest_framework.views import APIView
from rest_framework.response import Response

from .services import SearchService
from apps.search.serializers import FlightSearchRequestSerializer


class FlightSearchAPIView(APIView):

    def post(self, request):
        serializer = FlightSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = serializer.validated_data
        results = SearchService.search(payload)

        return Response({
            "success": True,
            "count": len(results),
            "results": results,
        })