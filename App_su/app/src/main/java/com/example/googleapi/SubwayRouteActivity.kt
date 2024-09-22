package com.example.googleapi

import CustomAdapter
import android.annotation.SuppressLint
import android.content.Context
import android.os.Bundle
import android.util.Log
import android.view.MotionEvent
import android.view.View
import android.view.inputmethod.InputMethodManager
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.googleapi.databinding.ActivitySubwayRouteBinding
import com.google.maps.DirectionsApi
import com.google.maps.GeoApiContext
import com.google.maps.GeocodingApi
import com.google.maps.model.*
import com.google.maps.model.Unit
import okhttp3.ResponseBody
import org.json.JSONException
import org.json.JSONObject
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class SubwayRouteActivity : AppCompatActivity() {

    data class CustomData(val id: Int, val value: Double)

    private lateinit var geoApiContext: GeoApiContext
    private lateinit var editTextStartStation: EditText
    private lateinit var editTextEndStation: EditText
    private lateinit var buttonFindRoute: Button
    private lateinit var textViewTransfer: TextView
    private lateinit var textViewDuration: TextView
    private lateinit var imageViewSubwayMap: ImageView
    private lateinit var binding: ActivitySubwayRouteBinding
    private lateinit var recyclerView1: RecyclerView
    private lateinit var recyclerView2: RecyclerView
    private lateinit var recyclerView3: RecyclerView
    private lateinit var rebutton: Button
    private lateinit var cAdapter: CustomAdapter
    private lateinit var layoutManager: LinearLayoutManager
    private lateinit var text1: TextView
    private lateinit var text2: TextView
    private lateinit var text3: TextView


    @SuppressLint("MissingInflatedId")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivitySubwayRouteBinding.inflate(layoutInflater)

        setContentView(R.layout.activity_subway_route)


        imageViewSubwayMap = findViewById(R.id.imageViewSubwayMap)
        imageViewSubwayMap.visibility = View.VISIBLE

        editTextStartStation = findViewById(R.id.editTextStartStation)
        editTextEndStation = findViewById(R.id.editTextEndStation)
        buttonFindRoute = findViewById(R.id.buttonFindRoute)
        textViewTransfer = findViewById(R.id.textViewTransfer)
        textViewDuration = findViewById(R.id.textViewDuration)

        recyclerView1 = findViewById(R.id.recycler_horizontal)
        recyclerView2 = findViewById(R.id.recycler_horizontal2)
        recyclerView3 = findViewById(R.id.recycler_horizontal3)
        rebutton = findViewById(R.id.buttonRefresh)


        geoApiContext = GeoApiContext.Builder()
            .apiKey("AIzaSyAOsQfD2tdX0-rC27Aai9KSmMYtVYDF5qc") // 여기에 Google Maps API 키를 입력하세요.
            .build()

        buttonFindRoute.setOnClickListener {
            findSubwayRoute()
            sendRequestToFlaskServer()
        }
        // 레이아웃에 대한 터치 이벤트 처리를 추가합니다.
        val layout = findViewById<View>(R.id.mylayout)
        layout.setOnTouchListener(object : View.OnTouchListener {
            override fun onTouch(v: View?, event: MotionEvent?): Boolean {
                hideKeyboard()
                return false
            }
        })

        // 버튼을 참조하고 클릭 이벤트를 설정
        val buttonRefresh = findViewById<Button>(R.id.buttonRefresh)
        buttonRefresh.setOnClickListener {
            // 리사이클러뷰 정보를 새로 고침
            refreshRecyclerViewData()
        }
    }

    @SuppressLint("ServiceCast")
    private fun hideKeyboard() {
        val inputManager = getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
        // 현재 포커스된 View의 윈도우 토큰을 사용하여 키보드를 숨깁니다.
        inputManager.hideSoftInputFromWindow(currentFocus?.windowToken, InputMethodManager.HIDE_NOT_ALWAYS)
    }

    private fun findSubwayRoute() {
        val startStationName = editTextStartStation.text.toString()
        val endStationName = editTextEndStation.text.toString()

        val startStationNameWithoutStation = startStationName.replace("역", "")
        val endStationNameWithoutStation = endStationName.replace("역", "")


        val startLocation = geocodeLocation(startStationName)
        val endLocation = geocodeLocation(endStationName)


        imageViewSubwayMap.visibility = View.GONE
        recyclerView2.visibility = View.VISIBLE
        recyclerView3.visibility = View.VISIBLE
        rebutton.visibility = View.VISIBLE


        if (startLocation != null && endLocation != null) {

            val request = DirectionsApi.newRequest(geoApiContext)
                .origin(startLocation)
                .destination(endLocation)
                .mode(TravelMode.TRANSIT)
                .transitMode(TransitMode.SUBWAY)
                .units(Unit.METRIC)
                .language("ko")

            val result = request.await()

            if (result.routes.isNotEmpty()) {

                val route = result.routes[0]
                val leg = route.legs[0]

                val transferStations = mutableListOf<String>()

                var totalDurationSeconds: Long = 0

                for (step in leg.steps) {
                    if (step.travelMode == TravelMode.TRANSIT && step.transitDetails.line.vehicle.type == VehicleType.SUBWAY) {
                        val stationName = step.transitDetails.departureStop.name
                        val stationNameWithoutLocation = stationName.substringBefore("역").replace("역", "")
                        if (stationNameWithoutLocation != startStationNameWithoutStation && stationNameWithoutLocation != endStationNameWithoutStation) {
                            transferStations.add(stationNameWithoutLocation)
                        }
                        totalDurationSeconds += step.duration.inSeconds.toLong()
                    }
                }

                val durationHours = totalDurationSeconds / 3600
                val durationMinutes = (totalDurationSeconds % 3600) / 60

                // 환승역 정보를 문자열로 변환 (출발 및 도착 역은 제외)
                // val transferStationsString = transferStations.filter { it != startStationName && it != endStationName }.joinToString(", ")
                val transferStationsString = transferStations.joinToString(", ")

                if (transferStations.isNotEmpty()) {
                    //  val transferStationsString = transferStations.joinToString(", ")
                    textViewTransfer.text = "환승역: $transferStationsString"

                    if (transferStations.size >= 2) {
                        recyclerView1.visibility = View.VISIBLE
                    } else {
                        recyclerView1.visibility = View.GONE
                    }
                } else {
                    textViewTransfer.text = "환승역이 없습니다."
                }

                textViewDuration.text = "소요 시간: ${durationHours}시간 ${durationMinutes}분"
            } else {
                textViewTransfer.text = "경로를 찾을 수 없습니다."
                textViewDuration.text = ""
            }
        } else {
            textViewTransfer.text = "출발 또는 도착 지역을 찾을 수 없습니다."
            textViewDuration.text = ""
        }

    }

    private fun geocodeLocation(locationName: String): LatLng? {
        val geocodingResult = GeocodingApi.geocode(geoApiContext, locationName).await()

        if (geocodingResult.isNotEmpty()) {
            val result = geocodingResult[0]
            return result.geometry.location
        }

        return null
    }
    // Retrofit을 사용하여 Flask 서버로 GET 요청을 보내고 응답을 처리하는 부분
    private fun sendRequestToFlaskServer() {
        val retrofit = Retrofit.Builder()
            .baseUrl("http://192.168.161.150:8000") // Flask 서버의 URL을 여기에 입력하세요.
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        val apiService = retrofit.create(ApiService::class.java) // ApiService는 Flask API와 관련된 Retrofit 인터페이스입니다.

        apiService.getDbValues().enqueue(object : Callback<ResponseBody> {
            override fun onResponse(call: Call<ResponseBody>, response: Response<ResponseBody>) {
                if (response.isSuccessful) {
                    val jsonResponse = response.body()?.string()
                    if (jsonResponse != null) {
                        Log.d("ServerResponse", jsonResponse)
                    } // 이 줄을 추가하여 서버 응답을 로그에 출력
                    processJsonResponse(jsonResponse)
                } else {
                    Log.e("ServerResponseError", "Server response was not successful")
                    // 응답이 실패한 경우에 대한 처리를 추가할 수 있습니다.
                }
            }

            override fun onFailure(call: Call<ResponseBody>, t: Throwable) {
                // 통신 실패 시에 대한 처리를 추가할 수 있습니다.
                Log.e("ServerResponseError", "Failed to make a server request: ${t.message}")
            }
        })
    }

    // Flask 서버에서 받은 JSON 응답을 처리하는 함수
    private fun processJsonResponse(jsonResponse: String?) {
        try {
            val jsonObject = JSONObject(jsonResponse)
            // val dbValuesArray = jsonObject.getJSONArray("db_values")
            val dbValuesArray3 = jsonObject.getJSONArray("db_values3")
            val dbValuesArray4 = jsonObject.getJSONArray("db_values4")

            val customDataList = ArrayList<CustomData>()
            val customDataList3 = ArrayList<CustomData>()
            val customDataList4 = ArrayList<CustomData>()

            /* for (i in 0 until dbValuesArray.length()) {
                 val valueObject = dbValuesArray.getJSONObject(i)
                 val value = valueObject.getDouble("value")
                 // CustomData 객체를 생성하고 리스트에 추가
                 val customData = CustomData(i, value)
                 customDataList.add(customData)
             }*/
            for (i in 0 until dbValuesArray3.length()) {
                val valueObject = dbValuesArray3.getJSONObject(i)
                val value = valueObject.getDouble("value3")
                val customData = CustomData(i, value)
                customDataList3.add(customData)
            }

            for (i in 0 until dbValuesArray4.length()) {
                val valueObject = dbValuesArray4.getJSONObject(i)
                val value = valueObject.getDouble("value4")
                val customData = CustomData(i, value)
                customDataList4.add(customData)
            }
            // Set the data for RecyclerViews
            val adapter1 = CustomAdapter(customDataList)
            recyclerView1.layoutManager = LinearLayoutManager(this, LinearLayoutManager.HORIZONTAL, false)
            recyclerView1.adapter = adapter1

            val adapter2 = CustomAdapter(customDataList3)
            recyclerView2.layoutManager = LinearLayoutManager(this, LinearLayoutManager.HORIZONTAL, false)
            recyclerView2.adapter = adapter2

            val adapter3 = CustomAdapter(customDataList4)
            recyclerView3.layoutManager = LinearLayoutManager(this, LinearLayoutManager.HORIZONTAL, false)
            recyclerView3.adapter = adapter3

        } catch (e: JSONException) {
            e.printStackTrace()
            // JSON 파싱 오류 처리를 수행할 수 있습니다.
        }
    }

    // 리사이클러뷰 정보를 새로 고침하는 함수
    private fun refreshRecyclerViewData() {
        // 여기에서 리사이클러뷰의 어댑터에 새로운 데이터를 설정하거나, 데이터를 다시 불러오는 작업을 수행하세요.
        // 예를 들어, API를 호출하여 데이터를 다시 가져올 수 있습니다.
        // 데이터를 변경한 후, 어댑터에 데이터 변경을 알리는 메서드를 호출하여 리사이클러뷰를 새로 고침합니다.
    }
}


