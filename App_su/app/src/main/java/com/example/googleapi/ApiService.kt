package com.example.googleapi
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.http.GET

interface ApiService {
    // Flask 서버의 API 엔드포인트와 요청 방식(GET, POST 등)을 여기에 정의합니다.
    // 예를 들어, Flask 서버의 특정 엔드포인트로 GET 요청을 보내려면 다음과 같이 정의할 수 있습니다.

    @GET("get_db_values") // 엔드포인트 URL을 설정합니다.
    fun getDbValues(): Call<ResponseBody> // 응답 데이터 유형을 설정합니다.
}