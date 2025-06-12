package com.example.demo; // 注意换成你的包名

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/hello")
    public String hello(@RequestParam(name = "name", defaultValue = "world") String name) {
        return "Hello " + name;
    }
}