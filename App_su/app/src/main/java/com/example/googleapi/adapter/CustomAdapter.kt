import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import com.example.googleapi.R
import com.example.googleapi.SubwayRouteActivity



class CustomAdapter(private val customDataList: List<SubwayRouteActivity.CustomData>) : RecyclerView.Adapter<CustomAdapter.CustomViewHolder>() {



    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CustomViewHolder {
        return CustomViewHolder(
            LayoutInflater.from(parent.context)
                .inflate(R.layout.item_list, parent, false)
        )
    }

    override fun onBindViewHolder(holder: CustomViewHolder, position: Int) {
        val data = customDataList[position]
        holder.bind(data)
        // 조건에 따라 backgroundTint 변경
       if (data.value > 10.5) {
            holder.imgView.backgroundTintList = ContextCompat.getColorStateList(holder.imgView.context, R.color.green)
        } else if (8.0 < data.value){
            holder.imgView.backgroundTintList = ContextCompat.getColorStateList(holder.imgView.context, R.color.yellow)
        }else{
            holder.imgView.backgroundTintList = ContextCompat.getColorStateList(holder.imgView.context, R.color.red)
        }
    }

    override fun getItemCount(): Int {
        return customDataList.size
    }

    class CustomViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val imgView: ImageView = view.findViewById(R.id.item_img)
        val txtView: TextView = view.findViewById(R.id.item_name)

        fun bind(data: SubwayRouteActivity.CustomData) {
            txtView.text = "${data.id+1}호차"
        }
    }
}