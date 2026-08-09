package uz.ganikhodjaev.weather.ui.main

import android.os.Bundle
import android.view.View
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import uz.ganikhodjaev.weather.App
import uz.ganikhodjaev.weather.R
import uz.ganikhodjaev.weather.data.model.WeatherDataModel
import uz.ganikhodjaev.weather.databinding.FragmentMainBinding

class MainFragment : Fragment(R.layout.fragment_main) {


    private var _binding: FragmentMainBinding? = null
    private val binding get() = _binding!!


    private val viewModel by viewModels<MainViewModel> { App.appComponent.getViewModelFactory() }

    private val adapter by lazy { MainAdapter() }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentMainBinding.bind(view)
        binding.rvList.adapter = adapter
        viewModel.weatherEvent.onEach(::handleData).launchIn(viewLifecycleOwner.lifecycleScope)


    }

    private fun handleData(weatherDataModel: WeatherDataModel) {

        adapter.submitList(weatherDataModel.listData)
    }


}