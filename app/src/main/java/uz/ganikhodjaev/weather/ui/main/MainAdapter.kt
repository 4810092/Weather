package uz.ganikhodjaev.weather.ui.main

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView.ViewHolder
import uz.ganikhodjaev.weather.data.model.ListModel
import uz.ganikhodjaev.weather.databinding.ItemMainBinding
import java.text.SimpleDateFormat
import java.util.Locale

class MainAdapter :
    ListAdapter<ListModel, MainAdapter.MainVH>(object : DiffUtil.ItemCallback<ListModel>() {
        override fun areItemsTheSame(oldItem: ListModel, newItem: ListModel): Boolean {
            return oldItem == newItem
        }

        override fun areContentsTheSame(oldItem: ListModel, newItem: ListModel): Boolean {
            return oldItem == newItem
        }
    }) {


    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) = MainVH(
        ItemMainBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
    )

    override fun onBindViewHolder(holder: MainVH, position: Int) = holder.onBind(getItem(position))


    class MainVH(private val binding: ItemMainBinding) : ViewHolder(binding.root) {
        fun onBind(item: ListModel) {
            with(binding) {

                val dateTime = SimpleDateFormat("dd MMM yyyy HH:mm", Locale.getDefault())

                tvDateTime.text = dateTime.format(item.dt?.times(1000))
                tv.text = item.toString()
            }
        }
    }
}